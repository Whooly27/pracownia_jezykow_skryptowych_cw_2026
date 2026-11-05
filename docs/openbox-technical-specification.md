# OpenBox — Technical Specification

## 1. Access model

- Each folder tree has one **owner**. Only **files** are shared, never folders.
- A permission grant gives one user a set of permissions on one file. Every grant includes `view`, which lets you see and download the file.
- Grantees see the file's folder path. Inside those folders they only see what was shared with them. These folders are reached from Sharing; they never appear in the grantee's own top level.
- You can only pass on permissions you hold. The owner holds all of them, and only the owner can upload into their folders.
- Access and links someone gave stay when they lose `share` or `link` or are removed.

| Permission | Allows |
|---|---|
| `view` | See and download |
| `edit` | Replace the contents |
| `rename` | Rename |
| `delete` | Delete permanently, for everyone |
| `share` | Invite, change or remove people |
| `link` | Create or delete share links |

A grant is created in one of two ways, shown as `via` in the API:

| | `direct` | `link` |
|---|---|---|
| How | Someone with `share` invites an existing account by email | Someone with `link` creates a URL and sends it |
| Who gets it | That one person | Anyone signed in who opens the URL |
| When it starts | Immediately | When the person opens the link and signs in |
| Expiry | None | The URL stops accepting new people at `expires_at`; people who already joined keep their access |
| Removing it | Remove the person | Remove the person, or delete the link to remove everyone who joined through it |

A link grant's `granted_by` is the link's creator. Someone who gets access both ways has two grants and holds the permissions of both; `permissions` in the API is the union. When the owner removes the person, both go; anyone else removes only the grants they gave. Deleting the link removes only what the link gave.

The app shows permission sets by name: **Can view** = `view`, **Can edit** = `view` + `edit` + `rename`, **Full access** = all six. Any other set lists what it allows besides `view`, calling `edit` “replace”, e.g. **Can share** or **Can replace, share**.

## 2. Flows

### Open a folder

The app asks for the folder's first 50 items, then the next 50 each time the user scrolls to the end.

![Open a folder](openbox-diagrams/open-folder-v5.svg)

### Upload a file

The browser sends the bytes straight to storage. The API hands out a signed upload URL that accepts at most the declared size and only the declared type, then marks the file ready.

![Upload a file](openbox-diagrams/upload-a-file-v3.svg)

### Download a file

The API checks that the user can see the file and returns a signed storage URL valid for 60 seconds. The browser downloads straight from storage.

![Download a file](openbox-diagrams/download-a-file-v3.svg)

### Open a share link

Opening a link needs an account. Someone who isn't signed in goes through sign-in and lands back on the link, which then grants them access.

![Open a share link](openbox-diagrams/open-a-share-link-v5.svg)

### Download a folder

A folder is zipped in the background. The app polls the job and downloads the zip when it's ready. An hourly job deletes zips older than an hour.

![Download a folder](openbox-diagrams/download-a-folder-v3.svg)

### Delete files and folders

Deleting is permanent for everyone, so the app asks for confirmation first. Deleting a folder deletes everything in it. The stored bytes are removed afterwards by a background job.

![Delete files and folders](openbox-diagrams/delete-files-and-folders-v4.svg)

## 3. Screens

### Landing

Signed-out home page.

| Desktop | Mobile |
|---|---|
| ![Landing, desktop](openbox-wireframes/view-01-landing-desktop.svg) | ![Landing, mobile](openbox-wireframes/view-01-landing-mobile.svg) |

### Sign in

Cognito Managed Login with OpenBox branding. Sign-up (name, email, password) and the email code are Cognito's pages too, and so are their errors, such as a wrong password.

| Desktop | Mobile |
|---|---|
| ![Sign in, desktop](openbox-wireframes/view-02-sign-in-desktop.svg) | ![Sign in, mobile](openbox-wireframes/view-02-sign-in-mobile.svg) |

### Files: folder selected

Selecting items opens a toolbar at the bottom (desktop) or an action sheet (mobile) with only the actions the selection allows. On mobile, + opens Upload and New folder; ⋯ on a row opens the same sheet.

| Desktop | Mobile |
|---|---|
| ![Files: folder selected, desktop](openbox-wireframes/view-03-files-folder-desktop.svg) | ![Files: folder selected, mobile](openbox-wireframes/view-03-files-folder-mobile.svg) |

### Files: file selected

The owner gets every action. Replace asks first, then uploads the new contents through the upload panel.

| Desktop | Mobile |
|---|---|
| ![Files: file selected, desktop](openbox-wireframes/view-04-files-file-desktop.svg) | ![Files: file selected, mobile](openbox-wireframes/view-04-files-file-mobile.svg) |

### Upload

Upload opens the file picker; files can also be dropped on the list. Each file uploads on its own: finished files join the list, rejected ones show the reason, and the rest keep going. Type and size are checked against `upload_policy` before Start upload, so each rejected file gets its own reason. On mobile, progress shows in a bottom sheet above the tab bar. A failed or expired upload shows Try again. Cancel stops an upload; its reserved name frees up when it expires. While files are dragged over the list, it shows a dashed outline and “Drop to upload to Design”.

| Desktop | Mobile |
|---|---|
| ![Upload, desktop](openbox-wireframes/view-05-upload-desktop.svg) | ![Upload, mobile](openbox-wireframes/view-05-upload-mobile.svg) |

### New folder

Empty names, names over 255 characters and names with / are caught as you type; a taken name is caught when the server answers. Rename uses the same dialog, filled with the current name.

| Desktop | Mobile |
|---|---|
| ![New folder, desktop](openbox-wireframes/view-06-new-folder-desktop.svg) | ![New folder, mobile](openbox-wireframes/view-06-new-folder-mobile.svg) |

### Zip download

A folder, or several files as “Design (3 files).zip”, is zipped in the background; the same panel (a bottom sheet on mobile) shows progress and the download starts when the zip is ready. A zip that fails or is too big says why; a storage failure shows Try again. Cancel (× on desktop) stops waiting; the job and its zip expire on their own. A finished zip downloads and leaves the panel.

| Desktop | Mobile |
|---|---|
| ![Zip download, desktop](openbox-wireframes/view-07-download-desktop.svg) | ![Zip download, mobile](openbox-wireframes/view-07-download-mobile.svg) |

### Confirm delete

Delete always asks first and names what goes. On mobile the same dialog fills the width.

| Desktop | Mobile |
|---|---|
| ![Confirm delete, desktop](openbox-wireframes/view-08-confirm-delete-desktop.svg) | ![Confirm delete, mobile](openbox-wireframes/view-08-confirm-delete-mobile.svg) |

### Sharing: file you can share

Kate holds share on Q4 Budget.xls. Shared by me shows Members instead of Owner. A file at its owner's top level shows no Location. Clicking a Location opens that folder with only what was shared with you, and without New folder or Upload.

| Desktop | Mobile |
|---|---|
| ![Sharing: file you can share, desktop](openbox-wireframes/view-09-shared-can-share-desktop.svg) | ![Sharing: file you can share, mobile](openbox-wireframes/view-09-shared-can-share-mobile.svg) |

### Sharing: view-only file

Kate can only view Brand guide.pdf.

| Desktop | Mobile |
|---|---|
| ![Sharing: view-only file, desktop](openbox-wireframes/view-10-shared-view-only-desktop.svg) | ![Sharing: view-only file, mobile](openbox-wireframes/view-10-shared-view-only-mobile.svg) |

### Share: people

Share shows when you hold share or link; with only link, People is read-only. People with access scroll inside a fixed-height list; each person's menu changes their access, its last option opens the checkboxes from Invite people, and × removes the access you gave them (the owner removes all of it). Options below what the member keeps from links or from other people's grants are disabled. On mobile, rows leave out who invited them. Rows for people you gave no access to, directly or through your links, show their access as text, with no menu or ×.

| Desktop | Mobile |
|---|---|
| ![Share: people, desktop](openbox-wireframes/view-11-share-people-desktop.svg) | ![Share: people, mobile](openbox-wireframes/view-11-share-people-mobile.svg) |

### Invite people

Kate holds view and share, so those are all she can give. Invites go to existing accounts. Cancel returns to Share: people. View can't be unticked.

| Desktop | Mobile |
|---|---|
| ![Invite people, desktop](openbox-wireframes/view-12-add-people-desktop.svg) | ![Invite people, mobile](openbox-wireframes/view-12-add-people-mobile.svg) |

### Share: links

Without link, the list is read-only and Create link is hidden. Delete shows only on links you created; the owner sees it on every link.

| Desktop | Mobile |
|---|---|
| ![Share: links, desktop](openbox-wireframes/view-13-share-links-desktop.svg) | ![Share: links, mobile](openbox-wireframes/view-13-share-links-mobile.svg) |

### Create link

Pick what the link allows and when it expires: 1 day, 7 days or 30 days from now, never, or the end of a chosen day in your time zone. Days before today can't be picked. On mobile, the date opens the app's own calendar sheet.

| Desktop | Mobile |
|---|---|
| ![Create link, desktop](openbox-wireframes/view-14-create-link-desktop.svg) | ![Create link, mobile](openbox-wireframes/view-14-create-link-mobile.svg) |

### Link created

Done (× on mobile) closes it; the link then shows in Share: links, without its URL.

| Desktop | Mobile |
|---|---|
| ![Link created, desktop](openbox-wireframes/view-15-link-created-desktop.svg) | ![Link created, mobile](openbox-wireframes/view-15-link-created-mobile.svg) |

### Other confirmations

Replace and every action that removes access ask first too. On mobile each is the same dialog at full width. Delete a link names how many people still have access through it, and with none says only that it stops working. When someone other than the owner removes a person, the text reads “Robin loses the access you gave.” Changing someone's access applies at once.

| Desktop | Mobile |
|---|---|
| ![Other confirmations, desktop](openbox-wireframes/view-16-confirmations-desktop.svg) | ![Other confirmations, mobile](openbox-wireframes/view-16-confirmations-mobile.svg) |

### Search

Typing 2+ characters replaces the list with matching names from your files and files shared with you. Location shows where each result lives. Clearing the box goes back to the folder you were in.

| Desktop | Mobile |
|---|---|
| ![Search, desktop](openbox-wireframes/view-17-search-desktop.svg) | ![Search, mobile](openbox-wireframes/view-17-search-mobile.svg) |

### Empty states

Every list has an empty state: your top level, a folder, Shared with me, Shared by me, search and Share: links. New folder and Upload show only in your own folders; Create link needs link.

| Desktop | Mobile |
|---|---|
| ![Empty states, desktop](openbox-wireframes/view-18-empty-desktop.svg) | ![Empty states, mobile](openbox-wireframes/view-18-empty-mobile.svg) |

### Loading

Lists show placeholder rows until the first page arrives, and the Share dialog uses the same rows. Opening a share link shows the mobile page while it's redeemed; desktop shows the same in the page centre. A button that sends a request shows a spinner and ignores clicks until it answers. Scrolling to the end adds placeholder rows under the list; if that page fails, a Try again row replaces them, and after `invalid_after` the list reloads from the top.

| Desktop | Mobile |
|---|---|
| ![Loading, desktop](openbox-wireframes/view-19-loading-desktop.svg) | ![Loading, mobile](openbox-wireframes/view-19-loading-mobile.svg) |

### Page errors

A failed load offers Try again. A folder you can't see, a Share dialog you lost access to, and a link that expired, was deleted, was never valid or no longer lets you in each say why and offer a way out.

| Desktop | Mobile |
|---|---|
| ![Page errors, desktop](openbox-wireframes/view-20-errors-desktop.svg) | ![Page errors, mobile](openbox-wireframes/view-20-errors-mobile.svg) |

### Action and input errors

A failed action shows a toast naming each item that failed, from its error message or, for an id, the name the app already shows; in bulk actions, the items that succeeded stay done. Input errors show under the field. After a 401 the app signs in again and returns to the same page.

| Desktop | Mobile |
|---|---|
| ![Action and input errors, desktop](openbox-wireframes/view-21-action-errors-desktop.svg) | ![Action and input errors, mobile](openbox-wireframes/view-21-action-errors-mobile.svg) |

## 4. API

Base URL `https://<domain>/api/v1`. Every request carries the session cookie set by sign-in. Every `POST` carries an `Idempotency-Key`; repeating a request with the same key returns the first response instead of doing the work twice. Keys are per user and kept for 24 hours. A `POST` without a key gets `400 missing_idempotency_key`; reusing a key for a different request gets `422 idempotency_key_reused`, and while the first request is still running, `409 request_in_progress`.

### 4.1 Files

#### List files — `GET /files`

Lists one page of files for any list screen: a folder, Shared with me, Shared by me, or search results. Pass at most one of `folder_id`, `shared_with_me`, `shared_by_me`, `q`; with none, it lists your top level.

```http
GET /api/v1/files?folder_id=7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83&sort=name&order=asc&limit=50
```

| Parameter | Values |
|---|---|
| `folder_id` | The folder to list |
| `shared_with_me` | `true`: files other people shared with you |
| `shared_by_me` | `true`: your files that someone else has access to |
| `q` | Name search, at least 2 characters. Matches your own files and folders, and files shared with you |
| `sort` | `name` (default) or `modified_at`; folders always come first, by name |
| `order` | `asc` (default) or `desc` |
| `limit` | 1–200, default 50 |
| `after` | Id of the last file or folder on the previous page; the next page starts right after it in the same `sort` and `order` |

```http
HTTP/1.1 200 OK

{
  "data": {
    "viewer": {
      "id": "a91d4e07-2c3b-4f58-8e6a-0b7c9d1e2f34",
      "display_name": "Kate",
      "email": "kate@acme.com"
    },
    "folder": {                           // null unless folder_id is set
      "id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83",
      "name": "Design",
      "path": [{ "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" }],
      "access": "path",                   // "owner" | "path" (seen through a shared file)
      "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" }
    },
    "upload_policy": null,                // set in your own folders and top level
    "items": [
      {                                         // Item: a file or a folder
        "id": "b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40",
        "kind": "file",                         // "file" | "folder"
        "name": "Q4 Budget.xls",
        "path": [                               // ancestors, top first; [] at the top level
          { "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" },
          { "id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83", "name": "Design" }
        ],
        "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
        "mime_type": "application/vnd.ms-excel",
        "size_bytes": 183223,                   // this and mime_type: null for folders
        "access": "granted",                    // "owner" | "granted" | "path"
        "permissions": ["view", "share"],       // what you may do
        "member_count": 6,                      // owner included; folder: people inside
        "modified_at": "2026-03-17T09:33:00Z",  // null for folders, like modified_by
        "modified_by": { "id": "c81d4f2e-6a3b-4d9c-8e1f-2b7a5c0d9e46", "display_name": "Jo" },
        "grants": [                             // [] unless it is shared with you
          {
            "via": "direct",
            "link_id": null,
            "permissions": ["view", "share"],
            "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
            "granted_at": "2026-10-30T12:00:00Z"
          }
        ]
      }
    ],
    "has_more": false                     // true when another page follows
  },
  "errors": []
}
```

An item's `permissions` are all six on files you own; `view`, `rename` and `delete` on folders you own; what you were given on shared files; and `view` on path folders. On a folder, `view` lets you open it; only its owner can download it. Share shows for files with `share` or `link`; Remove my access shows when `access` is `"granted"`; Download shows unless the selection includes a folder whose `access` is `"path"`.

In your own folders, `upload_policy` is:

```json
{
  "max_file_bytes": 26214400,
  "allowed_extensions": [
    "pdf", "png", "jpg", "jpeg", "gif", "webp", "doc", "docx", "xls", "xlsx",
    "ppt", "pptx", "odt", "ods", "odp", "rtf", "txt", "csv", "md"
  ]
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `404` | `not_found` | `folder_id` doesn't exist or you can't see it |
| `422` | `validation_failed` | More than one filter, `q` shorter than 2 characters, or a bad `sort`, `order` or `limit` |
| `422` | `invalid_after` | `after` isn't an item in this list, e.g. it was deleted; reload from the start |

#### Create folder — `POST /files/folders`

Creates a folder in one of your folders, or at your top level.

```http
POST /api/v1/files/folders
Idempotency-Key: 0b6f3d5e-91a2-4c8e-b7d4-2f1a9c6e8b30

{
  "folder_id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90",   // where to create it; null = top level
  "name": "Moodboards"
}
```

```http
HTTP/1.1 201 Created

{
  "data": {
    "id": "9d2e7b4a-1c6f-4e8b-a3d5-6f0c2e8b1a97",
    "kind": "folder",
    "name": "Moodboards",
    "path": [
      { "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" }
    ],
    "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "mime_type": null,
    "size_bytes": null,
    "access": "owner",
    "permissions": ["view", "rename", "delete"],
    "member_count": 1,
    "modified_at": null,
    "modified_by": null,
    "grants": []
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | `folder_id` isn't your folder |
| `404` | `not_found` | `folder_id` doesn't exist or you can't see it |
| `409` | `name_conflict` | The name is taken in that folder |
| `422` | `validation_failed` | Empty name, over 255 characters, or contains `/` |

#### Rename — `POST /files/{id}/rename`

Renames a file or folder; for a file, it updates `modified_at` and `modified_by`. Needs `rename`.

```http
POST /api/v1/files/f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68/rename
Idempotency-Key: 5d2c8a71-3e4f-4b9a-8c6d-1a7e0f3b9d52

{ "name": "Staff review 2026.docx" }
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68",
    "kind": "file",
    "name": "Staff review 2026.docx",
    "path": [
      { "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" },
      { "id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83", "name": "Design" }
    ],
    "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "size_bytes": 48211,
    "access": "owner",
    "permissions": ["view", "edit", "rename", "delete", "share", "link"],
    "member_count": 6,
    "modified_at": "2026-11-05T09:41:00Z",
    "modified_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "grants": []
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `rename` |
| `404` | `not_found` | The item doesn't exist or you can't see it |
| `409` | `name_conflict` | The name is taken in that folder |
| `415` | `unsupported_file_type` | For a file, the new extension isn't allowed or doesn't match its type |
| `422` | `validation_failed` | Empty name, over 255 characters, or contains `/` |

#### Delete — `POST /files/delete`

Deletes files and folders permanently, for everyone. Deleting a folder deletes everything in it and needs ownership; deleting a file needs `delete`. Each error's `message` names the item; for one that doesn't exist or you can't see, it gives the id you sent.

```http
POST /api/v1/files/delete
Idempotency-Key: 7f4e1b9c-0a3d-4e6b-8d2f-5c9a1e7b3f60

{ "ids": ["f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68", "c4e9a2d7-6f3b-4a18-8c5e-1b7d0f9a3e26"] }
```

```http
HTTP/1.1 200 OK

{
  "data": ["f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68"],
  "errors": [
    {
      "code": "not_found",
      "message": "Item c4e9a2d7-6f3b-4a18-8c5e-1b7d0f9a3e26 no longer exists."
    }
  ]
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `422` | `validation_failed` | `ids` is empty or has more than 100 entries |
| per item | `forbidden` | You don't have `delete`, or it's someone else's folder |
| per item | `not_found` | The item doesn't exist or you can't see it |

#### Remove my access — `POST /files/remove-access`

Removes files shared with you from your list by deleting all your grants on them, so you leave Share: people and `member_count`. The owner and everyone else keep their access. Each error's `message` gives the id you sent.

```http
POST /api/v1/files/remove-access
Idempotency-Key: 2a8d5f3c-7b1e-4c9a-a6d0-3e5f8b2c7a14

{ "ids": ["8e3b1f6d-2a9c-4d7e-b5f0-6c1a9d4e2b78"] }
```

```http
HTTP/1.1 200 OK

{ "data": ["8e3b1f6d-2a9c-4d7e-b5f0-6c1a9d4e2b78"], "errors": [] }
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `422` | `validation_failed` | `ids` is empty or has more than 100 entries |
| per item | `not_found` | The file isn't shared with you |

#### Download — `POST /files/download`

One file returns a signed storage URL, valid for 60 seconds, that saves the file under its real name. A folder or several files are zipped in the background; poll the job, then open its `result.url`. Unlike the other bulk endpoints, Download fails as a whole if any item is missing.

```http
POST /api/v1/files/download
Idempotency-Key: 9b3e6a1d-4c8f-4b2e-a7d5-1f0c3e9a6b82

{ "ids": ["b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40"] }
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "url": "https://store.blob.vercel-storage.com/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/Q4%20Budget.xls?download=1&token=4d7e9a2c1f8b",
    "expires_at": "2026-11-05T10:01:00Z"
  },
  "errors": []
}
```

```http
POST /api/v1/files/download
Idempotency-Key: 3c8f2a6d-9e1b-4d7a-b4c5-8f0e2d6a1b94

{ "ids": ["c4e9a2d7-6f3b-4a18-8c5e-1b7d0f9a3e26"] }
```

```http
HTTP/1.1 202 Accepted

{
  "data": {
    "id": "2e9c5a7f-3d1b-4b6e-8f4a-c0d7e2b9a153",
    "status": "queued",
    "processed_files": 0,
    "total_files": 450,
    "result": null
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | One of the items is a folder you don't own |
| `404` | `not_found` | One of the items doesn't exist or you can't see it |
| `413` | `zip_too_large` | The selection is over 10 GB |
| `422` | `validation_failed` | `ids` is empty or has more than 100 entries |

### 4.2 Uploads

#### Start upload — `POST /uploads`

Reserves new files in one of your folders, or at your top level (`folder_id: null`), and returns where to send each one's bytes. Each name stays reserved until the upload finishes or expires; starting the same name again replaces your own pending upload. Rejected files are listed in `errors`, each `message` naming the file; the rest can be uploaded, and if all are rejected the response is still `201` with `data: []`.

```http
POST /api/v1/uploads
Idempotency-Key: 4e7c1a9b-2d5f-4a3e-8b6c-0d9f2e5a7c31

{
  "folder_id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83",
  "files": [
    {
      "name": "Q1 Budget.xlsx",
      "size_bytes": 201734,
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    {
      "name": "Brand brief v2.pdf",
      "size_bytes": 1992294,
      "mime_type": "application/pdf"
    }
  ]
}
```

```http
HTTP/1.1 201 Created

{
  "data": [
    {                                     // Upload — the same object everywhere below
      "id": "4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73",
      "name": "Q1 Budget.xlsx",
      "put_url": "https://store.blob.vercel-storage.com/uploads/4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73?token=8f2c1a9e5d3b",
      "put_headers": {
        "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      },
      "expires_at": "2026-11-05T10:15:00Z"
    },
    {
      "id": "6d1f8a3c-2e7b-4c9d-b5a0-3f8e1c6d9b42",
      "name": "Brand brief v2.pdf",
      "put_url": "https://store.blob.vercel-storage.com/uploads/6d1f8a3c-2e7b-4c9d-b5a0-3f8e1c6d9b42?token=c41e7b2a9d05",
      "put_headers": { "content-type": "application/pdf" },
      "expires_at": "2026-11-05T10:15:00Z"
    }
  ],
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | `folder_id` isn't your folder |
| `404` | `not_found` | `folder_id` doesn't exist or you can't see it |
| `422` | `validation_failed` | `files` is empty or has more than 100 entries, or a malformed body |
| per file | `unsupported_file_type` | The extension isn't allowed or doesn't match `mime_type` |
| per file | `file_too_large` | Over 25 MB |
| per file | `name_conflict` | The folder already has that name |
| per file | `validation_failed` | Empty name, over 255 characters, or contains `/` |

#### Replace contents — `POST /files/{id}/replace`

Starts an upload that replaces a file's contents. Finish it with `POST /uploads/{id}/complete`; the old contents are then deleted. Needs `edit`.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/replace
Idempotency-Key: 6a2f9d4c-1e7b-4d3a-9c8e-5b0a7f2d4e16

{ "size_bytes": 190112, "mime_type": "application/vnd.ms-excel" }
```

```http
HTTP/1.1 201 Created

{
  "data": {
    "id": "5e8a2c7f-9b3d-4f1a-8c6e-0d2b7f4a9c13",
    "name": "Q4 Budget.xls",
    "put_url": "https://store.blob.vercel-storage.com/uploads/5e8a2c7f-9b3d-4f1a-8c6e-0d2b7f4a9c13?token=2b7e4d91a6c0",
    "put_headers": { "content-type": "application/vnd.ms-excel" },
    "expires_at": "2026-11-05T10:20:00Z"
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `edit` |
| `404` | `not_found` | The file doesn't exist or you can't see it |
| `413` | `file_too_large` | Over 25 MB |
| `415` | `unsupported_file_type` | The type isn't allowed or doesn't match the file's extension |
| `422` | `validation_failed` | Malformed body, or the id is a folder |

#### Finish upload — `POST /uploads/{id}/complete`

Call after the `PUT` succeeds. Confirms the bytes arrived, then makes the file visible. A replace upload returns the same file, with the same id.

```http
POST /api/v1/uploads/4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73/complete
Idempotency-Key: 1d5b8e2a-9c3f-4e7d-b6a1-4f8c2d0e9a73
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "91f0c6b3-5d2e-4a7f-b4c9-8e3a1d6f2b05",
    "kind": "file",
    "name": "Q1 Budget.xlsx",
    "path": [
      { "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" },
      { "id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83", "name": "Design" }
    ],
    "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "size_bytes": 201734,
    "access": "owner",
    "permissions": ["view", "edit", "rename", "delete", "share", "link"],
    "member_count": 1,
    "modified_at": "2026-11-05T10:02:00Z",
    "modified_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "grants": []
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | For a replace, you no longer have `edit` |
| `404` | `not_found` | No such upload, it isn't yours, or its folder or the file it replaces was deleted |
| `409` | `upload_incomplete` | The bytes haven't arrived yet |
| `410` | `upload_expired` | The upload wasn't finished within 15 minutes; start again |

### 4.3 Sharing

#### File permissions — `GET /files/{id}/permissions`

Who has access to a file and through which links. Needs `share` or `link`. With `share` you can change members who have a grant whose `granted_by` is you; with `link` you can delete links whose `created_by` is you. The owner can change everyone except themselves, and delete any link.

```http
GET /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/permissions
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "viewer": {
      "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
      "display_name": "Alex",
      "email": "alex@acme.com"
    },
    "file": { "id": "b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40", "name": "Q4 Budget.xls" },
    "grantable_permissions": ["view", "edit", "rename", "delete", "share", "link"],
    "members": [
      {                                   // Member
        "user": {
          "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
          "display_name": "Alex",
          "email": "alex@acme.com"
        },
        "access": "owner",
        "permissions": ["view", "edit", "rename", "delete", "share", "link"],   // what they hold
        "grants": []                      // one per way they got access; [] for the owner
      },
      {
        "user": {
          "id": "a91d4e07-2c3b-4f58-8e6a-0b7c9d1e2f34",
          "display_name": "Kate",
          "email": "kate@acme.com"
        },
        "access": "granted",
        "permissions": ["view", "share"],
        "grants": [
          {
            "via": "direct",              // "direct" | "link"
            "link_id": null,              // the link they joined through; null for direct
            "permissions": ["view", "share"],
            "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
            "granted_at": "2026-10-30T12:00:00Z"
          }
        ]
      },
      {
        "user": {
          "id": "5c2e8f1a-7b4d-4a90-a3e1-6d8f0c2b9e57",
          "display_name": "Robin",
          "email": "robin@acme.com"
        },
        "access": "granted",
        "permissions": ["view"],
        "grants": [
          {
            "via": "direct",
            "link_id": null,
            "permissions": ["view"],
            "granted_by": { "id": "a91d4e07-2c3b-4f58-8e6a-0b7c9d1e2f34", "display_name": "Kate" },
            "granted_at": "2026-10-31T09:15:00Z"
          }
        ]
      },
      {
        "user": {
          "id": "c81d4f2e-6a3b-4d9c-8e1f-2b7a5c0d9e46",
          "display_name": "Jo",
          "email": "jo@acme.com"
        },
        "access": "granted",
        "permissions": ["view", "edit", "rename", "delete", "share", "link"],
        "grants": [
          {
            "via": "direct",
            "link_id": null,
            "permissions": ["view", "edit", "rename", "delete", "share", "link"],
            "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
            "granted_at": "2026-03-02T09:00:00Z"
          }
        ]
      },
      {
        "user": {
          "id": "47b2e9c1-5d8a-4f3e-9b6c-1a0e7d4f2c85",
          "display_name": "Dana",
          "email": "dana@acme.com"
        },
        "access": "granted",
        "permissions": ["view"],
        "grants": [
          {
            "via": "link",
            "link_id": "d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31",
            "permissions": ["view"],
            "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
            "granted_at": "2026-11-01T11:30:00Z"
          }
        ]
      },
      {
        "user": {
          "id": "e9a4c7d2-3b1f-4e6a-8c5d-7f0b2a9e6d14",
          "display_name": "Sam",
          "email": "sam@acme.com"
        },
        "access": "granted",
        "permissions": ["view"],
        "grants": [
          {
            "via": "direct",
            "link_id": null,
            "permissions": ["view"],
            "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
            "granted_at": "2026-10-30T12:05:00Z"
          }
        ]
      }
    ],
    "links": [
      {                                   // Link
        "id": "d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31",
        "permissions": ["view"],                // what the link gives
        "expires_at": "2026-12-05T22:59:59Z",   // null = never
        "redemption_count": 1,
        "created_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
        "created_at": "2026-11-01T09:00:00Z"
      },
      {
        "id": "7b2e4d9a-1c8f-4a3e-b6d5-0f9c2a7e4b61",
        "permissions": ["view", "edit", "rename"],
        "expires_at": null,
        "redemption_count": 0,
        "created_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
        "created_at": "2026-11-02T14:20:00Z"
      },
      {
        "id": "4f9c1a7e-6d2b-4e8a-9c3f-2b5d8e0a6c47",
        "permissions": ["view"],
        "expires_at": "2026-11-12T22:59:59Z",
        "redemption_count": 0,
        "created_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
        "created_at": "2026-11-04T08:10:00Z"
      }
    ]
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You have neither `share` nor `link` |
| `404` | `not_found` | The file doesn't exist or you can't see it |

#### Share with people — `POST /files/{id}/permissions`

Invites, changes and removes people in one request. Needs `share`, and you can give only permissions you hold. You change only the access you gave, directly or through your links; the owner changes anyone's. `add` creates or extends your direct grant to that person and `update` replaces it, creating one if they joined only through your link; the owner's `update` replaces all their direct grants with one from the owner. An existing grant keeps its `granted_at`. `remove` deletes the grants you gave; the owner's deletes all of them. What a link gives stays as the link gave it. People the owner removes can't rejoin through existing links until someone invites them again. Failed entries are listed in `errors`, each `message` naming the person by the email or `user_id` you sent; the rest are applied.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/permissions
Idempotency-Key: 5f9a2c7e-3b6d-4e1a-8f4c-7d2e0b5a9c38

{
  "add": [
    { "email": "lee@acme.com", "permissions": ["view", "edit", "rename"] },
    { "email": "pat@globex.com", "permissions": ["view"] }
  ],
  "update": [{ "user_id": "a91d4e07-2c3b-4f58-8e6a-0b7c9d1e2f34", "permissions": ["view"] }],
  "remove": ["5c2e8f1a-7b4d-4a90-a3e1-6d8f0c2b9e57"]
}
```

```http
HTTP/1.1 200 OK

{
  "data": [
    {
      "user": {
        "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
        "display_name": "Alex",
        "email": "alex@acme.com"
      },
      "access": "owner",
      "permissions": ["view", "edit", "rename", "delete", "share", "link"],
      "grants": []
    },
    {
      "user": {
        "id": "a91d4e07-2c3b-4f58-8e6a-0b7c9d1e2f34",
        "display_name": "Kate",
        "email": "kate@acme.com"
      },
      "access": "granted",
      "permissions": ["view"],
      "grants": [
        {
          "via": "direct",
          "link_id": null,
          "permissions": ["view"],
          "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
          "granted_at": "2026-10-30T12:00:00Z"
        }
      ]
    },
    {
      "user": {
        "id": "c81d4f2e-6a3b-4d9c-8e1f-2b7a5c0d9e46",
        "display_name": "Jo",
        "email": "jo@acme.com"
      },
      "access": "granted",
      "permissions": ["view", "edit", "rename", "delete", "share", "link"],
      "grants": [
        {
          "via": "direct",
          "link_id": null,
          "permissions": ["view", "edit", "rename", "delete", "share", "link"],
          "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
          "granted_at": "2026-03-02T09:00:00Z"
        }
      ]
    },
    {
      "user": {
        "id": "47b2e9c1-5d8a-4f3e-9b6c-1a0e7d4f2c85",
        "display_name": "Dana",
        "email": "dana@acme.com"
      },
      "access": "granted",
      "permissions": ["view"],
      "grants": [
        {
          "via": "link",
          "link_id": "d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31",
          "permissions": ["view"],
          "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
          "granted_at": "2026-11-01T11:30:00Z"
        }
      ]
    },
    {
      "user": {
        "id": "e9a4c7d2-3b1f-4e6a-8c5d-7f0b2a9e6d14",
        "display_name": "Sam",
        "email": "sam@acme.com"
      },
      "access": "granted",
      "permissions": ["view"],
      "grants": [
        {
          "via": "direct",
          "link_id": null,
          "permissions": ["view"],
          "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
          "granted_at": "2026-10-30T12:05:00Z"
        }
      ]
    },
    {
      "user": {
        "id": "2c7f9a4e-8b3d-4a1c-9e6f-5d0b8c2a7e39",
        "display_name": "Lee",
        "email": "lee@acme.com"
      },
      "access": "granted",
      "permissions": ["view", "edit", "rename"],
      "grants": [
        {
          "via": "direct",
          "link_id": null,
          "permissions": ["view", "edit", "rename"],
          "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
          "granted_at": "2026-11-05T09:55:00Z"
        }
      ]
    }
  ],
  "errors": [{ "code": "user_not_found", "message": "No OpenBox account uses pat@globex.com." }]
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `share` |
| `404` | `not_found` | The file doesn't exist or you can't see it |
| `422` | `validation_failed` | Malformed body, an unknown permission, or a set without `view` |
| per entry | `permission_escalation` | The entry gives a permission you don't hold |
| per entry | `user_not_found` | No OpenBox account with that email |
| per entry | `not_found` | `user_id` has no access to this file |
| per entry | `forbidden` | Any entry for the owner or yourself, or, unless you're the owner, `update` or `remove` for someone you gave no grant |

### 4.4 Links

#### Create link — `POST /files/{id}/links`

Creates a share link. Anyone who opens it and signs in gets its permissions. Needs `link`; the link can't give more than you hold. For a chosen day the app sends the end of that day in the user's time zone; dates are shown in local time.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/links
Idempotency-Key: 8c3d6f1a-2e9b-4a7c-b5d4-0e3f6a9c2b57

{
  "permissions": ["view", "edit", "rename"],
  "expires_at": "2026-12-24T22:59:59Z"    // null = never
}
```

```http
HTTP/1.1 201 Created

{
  "data": {
    "id": "e5c1a8d3-7b2f-4e9a-8d6c-1f3b5a7e9c20",
    "url": "https://<domain>/links/7Fq9xKpL2mZr",   // only in this response
    "permissions": ["view", "edit", "rename"],    // what the link gives
    "expires_at": "2026-12-24T22:59:59Z",
    "redemption_count": 0,
    "created_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "created_at": "2026-11-05T10:05:00Z"
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `link` |
| `403` | `permission_escalation` | The link would give a permission you don't hold |
| `404` | `not_found` | The file doesn't exist or you can't see it |
| `422` | `validation_failed` | `expires_at` is in the past, an unknown permission, or a set without `view` |

#### Delete link — `POST /links/{id}/delete`

The URL stops working and everyone who joined through it loses that access. Needs `link`; owners can delete any link, others only links they created.

```http
POST /api/v1/links/d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31/delete
Idempotency-Key: 0e7a4c2f-5d8b-4f1e-9a3c-6b2d8f0e4a95
```

```http
HTTP/1.1 204 No Content
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `link`, or it's not your link and you're not the owner |
| `404` | `not_found` | The link doesn't exist or you can't see it |

#### Redeem link — `POST /links/redeem`

Called by the web app's link page, `https://<domain>/links/{token}` (the URL people receive), after sign-in. Grants the link's permissions and returns the file, so the app can open its folder, or Shared with me when `path` is empty. Someone with access of another kind gets the link's grant added. For the owner, or someone who still holds this link's grant, it returns the file and changes nothing, even after the link expires.

```http
POST /api/v1/links/redeem
Idempotency-Key: 3b6e9a2d-7c1f-4d5b-8e0a-2f4c7d9b1e63

{ "token": "7Fq9xKpL2mZr" }
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40",
    "kind": "file",
    "name": "Q4 Budget.xls",
    "path": [
      { "id": "0d8e2b6a-4f1c-4b7e-9a3d-2c5f8e1b7a90", "name": "Acme Inc" },
      { "id": "7a1f3c9e-2b8d-4e6a-b5c1-9d0e4f2a6b83", "name": "Design" }
    ],
    "owner": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "mime_type": "application/vnd.ms-excel",
    "size_bytes": 190112,
    "access": "granted",
    "permissions": ["view", "edit", "rename"],
    "member_count": 7,
    "modified_at": "2026-11-05T10:06:00Z",
    "modified_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
    "grants": [
      {
        "via": "link",
        "link_id": "e5c1a8d3-7b2f-4e9a-8d6c-1f3b5a7e9c20",
        "permissions": ["view", "edit", "rename"],
        "granted_by": { "id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8", "display_name": "Alex" },
        "granted_at": "2026-11-05T10:12:00Z"
      }
    ]
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | Not signed in; go to `/auth/login?return_to=/links/7Fq9xKpL2mZr`, which comes back here |
| `403` | `forbidden` | The owner removed you after this link was created, and no one has invited you since |
| `404` | `not_found` | The token doesn't match any link, or the link's file was deleted |
| `410` | `link_expired` | The link is past its `expires_at` |
| `410` | `link_deleted` | The link was deleted |

### 4.5 Jobs

#### Job status — `GET /jobs/{id}`

Progress of a zip download. Poll every 1–5 s until `status` is `succeeded` or `failed`. Each poll of a succeeded job returns a new `result.url`, valid for 10 minutes, until the zip is deleted after an hour. A failed job's reason is in `errors`: `item_deleted` (a file was deleted while zipping) or `storage_failed`.

```http
GET /api/v1/jobs/2e9c5a7f-3d1b-4b6e-8f4a-c0d7e2b9a153
```

```http
HTTP/1.1 200 OK

{
  "data": {                               // Job
    "id": "2e9c5a7f-3d1b-4b6e-8f4a-c0d7e2b9a153",
    "status": "running",                  // "queued" | "running" | "succeeded" | "failed"
    "processed_files": 120,
    "total_files": 450,
    "result": null                        // { "url", "expires_at" } when "succeeded"
  },
  "errors": []
}
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "8b4f1d6c-7e2a-4d95-b3c8-1f6e9a0d4c27",
    "status": "failed",
    "processed_files": 2,
    "total_files": 3,
    "result": null
  },
  "errors": [{ "code": "item_deleted", "message": "A file was deleted while zipping." }]
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `404` | `not_found` | No such job, it isn't yours, or its zip was deleted after an hour |
