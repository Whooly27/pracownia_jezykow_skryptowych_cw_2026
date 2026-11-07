# OpenBox backend: płaskie pliki i upload

Data: 2026-11-07. Branch: `backend/upload` (PR 21). Źródło prawdy: `openbox-technical-specification (2).pdf`
z 7 listopada 2026 (trzecia wersja). Ten dokument opisuje, co ma powstać w tym branchu i dlaczego.

## Po co

Specyfikacja zmieniła się dwa razy od commitu `266a0f2`, który modelował foldery, sześć uprawnień
i udostępnianie bezpośrednie. Nowa wersja wyrzuca to wszystko. Branch ma dwa cele:

1. Doprowadzić domenę do zgodności z nową specyfikacją (sekcja 1 "Access model").
2. Dodać upload: `POST /uploads`, `POST /uploads/{id}/complete`, `POST /files/{id}/replace`
   (sekcja 4.2 "Uploads"), z atrapą Vercel Blob na potrzeby developmentu.

Kontekst projektu: zespół 6 osób, obrona bez pomocy AI. Kod ma być prosty do opowiedzenia,
funkcjonalność minimalna, testy tylko reguł domenowych.

## Cele

- Model danych 1:1 ze specyfikacją: plik ma jednego właściciela, nazwa unikalna per właściciel,
  trzy uprawnienia (`view`, `edit`, `delete`), dostęp tylko przez linki.
- Pełny flow uploadu da się przejść lokalnie: rezerwacja, PUT bajtów, complete. Branch jest tylko
  backendowy; sprawdzamy testami i curlem, frontend podłącza się osobno. `put_url` jest względny
  (`/api/v1/_blob/...`), więc przez proxy frontendu działa bez CORS.
- Odpowiedzi JSON w kształcie ze specyfikacji (`{"data": ..., "errors": [...]}`, kody błędów).
- Storage za interfejsem, żeby prawdziwy Vercel Blob dało się podpiąć bez ruszania widoków.

## Poza zakresem (kolejne branche)

- `GET /files` (listy, wyszukiwanie, paginacja), `POST /files/{id}/download`, rename, delete,
  remove-access, wszystkie endpointy linków.
- Logowanie przez Cognito. Na razie sesja Django: `request.user`, anonim dostaje 401. Bez
  dodatkowego widoku logowania: testy używają `force_login`, ręczne sprawdzenie przez sesję
  z `/admin/` (`createsuperuser`).
- Prawdziwy klient Vercel Blob.
- Sprzątanie wygasłych uploadów w tle (spec: brak background jobs; nazwa zwalnia się przez
  sprawdzenie `expires_at` przy kolejnej rezerwacji).

## Anty-cele

- Żadnego DRF, żadnych serializerów generycznych, żadnej warstwy "service" dla samego wzorca.
- Żadnej kompatybilności wstecz z modelem `Node`: nic nie jest na produkcji, migracje `0001`
  zastępujemy nowymi.
- Żadnych testów frameworka (że `auto_now_add` działa itp.).

## Część 1: domena po zmianach

### `apps/files/models.py`: `File` zamiast `Node`

Pola: `id` (UUID), `name` (max 255, bez `/`, nie puste), `owner` (FK, PROTECT), `mime_type`,
`size_bytes`, `storage_key` (klucz w storage, np. `files/{id}`), `modified_at`, `created_at`.
Unikalność: `(owner, name)` z kodem błędu `name_conflict`, z rozróżnianiem wielkości liter
(decyzja z 7.11). Bez `parent`, `kind`, `path()`, `modified_by`, `is_folder`, `is_file`.

`clean()` normalizuje `name` (strip) i sprawdza puste / `/`. Sprawdzenie unikalności zostaje w
`validate_constraints` przeniesione na pole `name`, jak dziś.

### `apps/sharing/permissions.py`

`Permission` = `view`, `edit`, `delete`. Znika `FOLDER_OWNER_PERMISSIONS`. `validate_permissions`
bez zmian w zasadzie (znane nazwy, bez powtórek, zawiera `view`).

### `apps/sharing/models.py`

`ShareLink` bez zmian poza FK na `File`. `Grant`: `file`, `user`, `link` (FK, CASCADE, wymagany),
`permissions`, `granted_at`. Znika `via`, `granted_by`, constraint `grant_link_matches_via`.
Unikalność: `(user, link)`. `clean()`: właściciel nie dostaje grantu; `permissions` grantu to kopia
`permissions` linku w chwili dołączenia (to reguła z redeem, w tym branchu tylko walidacja).

### `apps/sharing/access.py`

`access_for(user, file) -> Access | None`: właściciel ma wszystkie trzy; inaczej suma `permissions`
z grantów użytkownika na ten plik; brak grantów = `None`. Znika `"path"` i cała logika folderów.

Usunięcie linku (poza tym branchem) twardo kasuje jego granty i ustawia `deleted_at`, żeby redeem
mógł odpowiedzieć `410 link_deleted`. Dzięki temu `access_for` i `member_count` nie filtrują po
stanie linku: grant istnieje tylko wtedy, gdy daje dostęp.

### Testy

Testy folderów, `via`, `granted_by` i `FOLDER_OWNER_PERMISSIONS` do usunięcia. Zostają i są
dopasowane: unikalność nazwy per właściciel, walidacja nazwy, walidacja uprawnień, suma grantów,
właściciel bez grantu, wygasanie linku.

## Część 2: upload

### `apps/uploads/models.py`: `Upload`

Pola: `id` (UUID), `owner` (FK), `name`, `mime_type`, `size_bytes`, `storage_key`
(property `uploads/{id}`), `file` (FK na `File`, null: dla replace ustawione od początku, dla nowego
pliku po complete) z flagą `is_replace`, `expires_at` (`created_at` + 15 min), `completed_at`
(null do czasu complete), `created_at`.

Stan wynika z pól: pending = `completed_at is null and expires_at > now`, expired =
`completed_at is null and expires_at <= now`, done = `completed_at is not null`.

Rezerwacja nazwy (tylko dla nowych plików, nie dla replace): nazwa jest wolna, gdy właściciel
nie ma `File` o tej nazwie i nie ma pending `Upload` o tej nazwie. "Starting the same name again
replaces your own pending upload" (spec): nowy `POST /uploads` z tą samą nazwą usuwa poprzedni
pending upload tej nazwy i jego bajty z storage.

### `apps/uploads/policy.py`

`MAX_FILE_BYTES = 25 * 1024 * 1024` i tabela `rozszerzenie -> MIME` dla 19 rozszerzeń ze spec
(`pdf`, `png`, `jpg`, `jpeg`, `gif`, `webp`, `doc`, `docx`, `xls`, `xlsx`, `ppt`, `pptx`, `odt`,
`ods`, `odp`, `rtf`, `txt`, `csv`, `md`). `upload_policy()` zwraca słownik do odpowiedzi
`GET /files` (jeszcze nie używany, ale kształt zdefiniowany tu).

Walidacja jednego pliku, w tej kolejności (pierwszy błąd wygrywa, kod ze spec):

1. `validation_failed`: nazwa pusta, ponad 255 znaków, zawiera `/`; `size_bytes` nie jest
   dodatnią liczbą całkowitą. Puste `mime_type` to `unsupported_file_type` (nie zgadza się z
   rozszerzeniem), tak zachowuje się kod.
2. `unsupported_file_type`: rozszerzenie (ostatni segment po kropce, małe litery) spoza listy albo
   `mime_type` nie zgadza się z rozszerzeniem według tabeli. Mapowanie jest 1:1 (np. `jpg` i
   `jpeg` oba na `image/jpeg`; `md` na `text/markdown`; `csv` na `text/csv`).
3. `file_too_large`: `size_bytes > MAX_FILE_BYTES`.
4. `name_conflict`: nazwa zajęta (patrz rezerwacja).

### `apps/uploads/storage.py`: interfejs i atrapa

```python
class Storage(Protocol):
    def put_url(self, key: str, mime_type: str, size_bytes: int, expires_at: datetime) -> str: ...
    def head(self, key: str) -> StoredObject | None:   # size i mime, albo None gdy brak
    def copy(self, src: str, dst: str) -> None:        # z uploads/{id} do files/{id}, nadpisuje
    def delete(self, key: str) -> None:
```

Cztery operacje to dokładnie to, co daje Vercel Blob: podpisany PUT, `head`, `copy` i `delete`.
Vercel nie ma `move`, więc complete robi `copy` i potem `delete` klucza uploadu.

Jak to wygląda z prawdziwym Vercel Blob (dokumentacja "Vercel Signed URLs", stan na wrzesień 2026),
żeby atrapa nie odjechała od oryginału:

- Serwer woła `issueSignedToken({pathname, operations: ['put'], allowedContentTypes,
  maximumSizeInBytes, validUntil})`, a potem `presignUrl(token, {operation: 'put', pathname,
  access: 'private', allowedContentTypes, maximumSizeInBytes, allowOverwrite, validUntil})`.
  Wynik to jeden URL z podpisem w query (`vercel-blob-valid-until` itd.), bez żadnego nagłówka
  `Authorization`. Przeglądarka robi `fetch(url, {method: 'PUT', headers: {'content-type': ...},
  body})`. Storage sam odrzuca zły `Content-Type` i za duże ciało. To jest 1:1 `put_url` plus
  `put_headers` ze specyfikacji i tak samo zachowuje się atrapa.
- Sprawdzenie "czy bajty dotarły" to `head(pathname)`: zwraca `size` i `contentType`. Żadnego
  webhooka nie potrzeba (webhook `onUploadCompleted` i tak nie działa na localhost).
- Download to `presignUrl` z `operation: 'get'` i `validUntil` 60 sekund na prywatnym store;
  to samo, co spec opisuje w "Download a file". Poza tym branchem.
- Prawdziwy host to `https://<storeId>.private.blob.vercel-storage.com/<pathname>?...`; atrapa
  podmienia tylko host na nasze Django i podpis na HMAC z `SECRET_KEY`.

Ostrzeżenie na później: pakiet `vercel-blob` dla Pythona (0.5+) ma `put_blob`, `head_blob`,
`copy_blob`, `delete_blob`, ale nie ma podpisywania URL-i ani client uploads; to jest tylko w SDK
JS. Prawdziwa klasa `VercelBlobStorage` będzie więc musiała albo podpisywać URL-e sama (HTTP do
control API plus HMAC, wzorując się na źródłach SDK JS), albo dostać mały pomocnik w Node.
Interfejs `Storage` tego nie przesądza i nie trzeba tego rozstrzygać w tym branchu.

Atrapa `LocalBlobStorage` trzyma bajty na dysku w `settings.BLOB_ROOT` (dev: `apps/backend/blobdata/`,
w `.gitignore`; testy: katalog tymczasowy przez fixture). `put_url` zwraca adres w naszym Django:
`{BLOB_BASE_URL}/api/v1/_blob/{key}?token=...`, gdzie token to HMAC (`SECRET_KEY`) z
`key`, `mime_type`, `size_bytes`, `expires_at`. Widok `PUT /api/v1/_blob/<key>` sprawdza token,
odrzuca gdy `Content-Type` różni się od zadeklarowanego albo `Content-Length` przekracza
`size_bytes` (400), zapisuje bajty, odpowiada 200. Ten widok jest poza sesją (nie wymaga
logowania, chroni go token) i poza CSRF. Nazwa `_blob` sygnalizuje, że to element atrapy.

Wybór implementacji przez `settings.STORAGE_BACKEND` (ścieżka klasy), domyślnie atrapa.
Prawdziwy Vercel Blob to osobna klasa pod tym samym `Protocol`, poza tym branchem.

### Endpointy (`apps/uploads/views.py`, `apps/uploads/urls.py`, pod `api/v1/`)

Wspólne: tylko POST, JSON w ciele, 401 `unauthenticated` dla anonima, 422 `validation_failed`
dla niepoprawnego JSON. Widoki API są zwolnione z CSRF (`csrf_exempt`): cookie sesji ma
`SameSite=Lax`, co blokuje POST z obcej strony; wracamy do tego przy Cognito (decyzja z 7.11). Odpowiedź zawsze `{"data": ..., "errors": [...]}`. Błąd per plik:
`{"code": ..., "message": "<nazwa pliku>: <opis>"}`. Kody HTTP i błędów dokładnie jak w spec.

`POST /uploads` `{files: [{name, size_bytes, mime_type}]}`:
422 gdy `files` puste lub > 100. Każdy plik walidowany osobno; poprawne dostają `Upload` i wpis
w `data` (`id`, `name`, `put_url`, `put_headers: {"content-type"}`, `expires_at`), odrzucone wpis
w `errors`. Zawsze 201, nawet gdy `data: []`. Dwa pliki o tej samej nazwie w jednym żądaniu:
pierwszy przechodzi, drugi dostaje `name_conflict` (mój wybór, spec milczy).

`POST /files/{id}/replace` `{size_bytes, mime_type}`:
404 gdy plik nie istnieje lub `access_for` zwraca `None`; 403 gdy brak `edit`; 422 zły JSON;
415 gdy `mime_type` spoza listy albo niezgodny z rozszerzeniem nazwy pliku; 413 gdy za duży.
Tworzy `Upload` z `replaces=file`, `name=file.name`. 201 z obiektem Upload.

`POST /uploads/{id}/complete`:
404 gdy brak uploadu, nie należy do użytkownika, albo (replace) plik już nie istnieje;
410 `upload_expired` gdy wygasł; 403 gdy replace i użytkownik stracił `edit`;
409 `upload_incomplete` gdy `storage.head(key)` zwraca `None` albo rozmiar / typ różnią się od
zadeklarowanych. Sukces w jednej transakcji: dla nowego pliku tworzy `File`
(`storage_key=files/{file.id}`) i kopiuje bajty pod ten klucz; dla replace nadpisuje `mime_type`,
`size_bytes`, `modified_at` i kopiuje bajty na klucz pliku (stare nadpisane = "old contents
deleted"). Po udanym zapisie w bazie usuwa klucz uploadu ze storage. `completed_at = now`. Ponowne wywołanie na ukończonym uploadzie zwraca 200 z tym
samym plikiem (idempotentne, mój wybór: spec usunęła Idempotency-Key, a frontend pokazuje
"Try again"). Wyścig dwóch rezerwacji tej samej nazwy nie jest blokowany; gdy przy `complete`
`UniqueConstraint (owner, name)` odrzuci wstawienie, odpowiedź to 409 `name_conflict` (poza
tabelą spec, mój wybór).

Odpowiedź 200: obiekt File ze spec: `id`, `name`, `owner {id, display_name}`, `mime_type`,
`size_bytes`, `access` (`"owner"` | `"granted"`), `permissions`, `member_count` (1 + liczba
różnych użytkowników z grantami), `modified_at`, `grants` (`[]` dla właściciela; dla replace przez
grantee lista jego grantów: `link_id`, `permissions`, `granted_at`). Serializacja w jednej funkcji
`file_to_json(file, viewer)` w `apps/files/serializers.py`, do ponownego użycia w `GET /files`.

### Testy (reguły domenowe, pytest-django, `client.force_login`)

- policy: każdy z czterech kodów odrzucenia, `jpg`/`jpeg`, wielkość liter w rozszerzeniu,
  dokładnie 25 MB przechodzi, 25 MB + 1 nie.
- `POST /uploads`: mieszanka poprawnych i odrzuconych w jednym żądaniu; nazwa zajęta przez `File`;
  nazwa zajęta przez pending upload; ponowna rezerwacja tej samej nazwy podmienia pending;
  wygasły upload nie blokuje nazwy; pusta lista 422; anonim 401.
- `PUT /_blob`: zły token 403, zły content-type 400, za dużo bajtów 400, poprawny zapis 200.
- `complete`: brak bajtów 409, rozmiar inny niż zadeklarowany 409, wygasły 410, cudzy 404,
  sukces tworzy `File` z poprawnym `member_count` i `permissions`, drugi complete zwraca to samo.
- `replace`: brak `edit` 403, brak dostępu 404, zły typ 415, za duży 413, complete podmienia
  rozmiar i `modified_at`, zachowuje `id` i nazwę, plik usunięty przed complete 404.

## Co zostawiam budowniczemu

- Układ plików wewnątrz `apps/uploads` (jeden `views.py` czy osobne moduły).
- Jak wyciągać `request.user` i JSON w widokach (dekorator albo mała funkcja pomocnicza, byle jedna
  dla wszystkich widoków API; wyląduje w `apps/core`).
- Dokładne komunikaty `message` w błędach, byle nazywały plik.
