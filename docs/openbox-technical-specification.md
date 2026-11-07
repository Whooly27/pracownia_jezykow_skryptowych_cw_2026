# OpenBox — Technical Specification

## 1. Access model

- Each file has one **owner**. Only the owner can rename a file or share it.
- The owner shares a file by creating a **share link**. Anyone signed in who opens the link gets the permissions the link gives, on that one file. Files can't be shared with a person directly; links are the only way to get access.
- People who got a file through a link can't share it further: files shared with you have no Share, and you can't create links or pass your access on.
- Every link gives `view`.

| Permission | Allows |
|---|---|
| `view` | See and download |
| `edit` | Replace the contents |
| `delete` | Delete permanently, for everyone |

A link stops accepting new people at `expires_at`; people who already joined keep their access. Someone who joins through several links holds the permissions of all of them, and `permissions` in the API is the union. Sharing is managed only through links: the owner deletes a link to remove everyone who joined through it. There is no list of people to manage.

The app shows permission sets by name: **Can view** = `view`, **Can edit** = `view` + `edit`, **Can delete** = `view` + `delete`, **Full access** = all three.

## 2. Flows

### List files

The app asks for the first 50 files, then the next 50 each time the user scrolls to the end.

![List files](openbox-diagrams/list-files-v1.svg)

### Upload a file

Files are uploaded one at a time. The user picks a file in the Upload dialog, which checks it against `upload_policy` first. The browser sends the bytes straight to storage. The API hands out a signed upload URL that accepts at most the declared size and only the declared type, then marks the file ready.

![Upload a file](openbox-diagrams/upload-a-file-v5.svg)

### Download a file

Files are downloaded one at a time. The API checks that the user can see the file and returns a signed storage URL valid for 60 seconds. The browser downloads straight from storage.

![Download a file](openbox-diagrams/download-a-file-v4.svg)

### Open a share link

Opening a link needs an account. Someone who isn't signed in goes through sign-in and lands back on the link, which then grants them access.

![Open a share link](openbox-diagrams/open-a-share-link-v7.svg)

### Delete a file

Deleting is permanent for everyone, so the app asks for confirmation first. The API removes the stored bytes in the same request.

![Delete a file](openbox-diagrams/delete-a-file-v1.svg)

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

### Files: file selected

My files lists every file you own; a Shared badge marks the ones someone else has access to (`is_shared`). Clicking a row selects that file, and only one file can be selected at a time. The selection opens a toolbar at the bottom (desktop) or an action sheet (mobile) with only the actions the file allows; clicking the row again clears it. On mobile, + opens Upload; ⋯ on a row opens the same sheet. The owner gets every action, and only the owner sees Share. Replace asks first, then uploads the new contents through the upload dialog.

| Desktop | Mobile |
|---|---|
| ![Files: file selected, desktop](openbox-wireframes/view-03-files-file-desktop.svg) | ![Files: file selected, mobile](openbox-wireframes/view-03-files-file-mobile.svg) |

### Upload

Upload opens this dialog (a full page on mobile) for one file at a time. The file is dropped on it or picked with browse (Choose a file on mobile); picking another replaces it, and × clears it. It is checked against `upload_policy` as soon as it's chosen, so a wrong type or a file over 25 MB shows the reason under it and Upload stays disabled. Dragging a file over the list shows a dashed outline and “Drop to upload”, and dropping it opens this dialog; dropping several files shows “Upload one file at a time.”

| Desktop | Mobile |
|---|---|
| ![Upload, desktop](openbox-wireframes/view-04-upload-desktop.svg) | ![Upload, mobile](openbox-wireframes/view-04-upload-mobile.svg) |

### Upload states

The file field changes as the upload goes, and the dialog's buttons change with it. Ready: the chosen file with × to clear it, and Upload. Uploading: progress, percentage and bytes sent, while the button shows a spinner and ignores clicks; Cancel (× on mobile) stops the upload, and its reserved name frees up when it expires. Error: the field turns red and says why, such as a failed or expired upload or a file the server rejects, with Try again; a wrong type or a file over 25 MB shows here before uploading, with Upload disabled. Uploaded: a check, and the file has joined the list; Done closes the dialog. On mobile the buttons sit in the bar at the bottom of the page.

| Desktop | Mobile |
|---|---|
| ![Upload states, desktop](openbox-wireframes/view-05-upload-states-desktop.svg) | ![Upload states, mobile](openbox-wireframes/view-05-upload-states-mobile.svg) |

### Rename

Only the owner can rename a file. Rename opens a dialog filled with the current name. Empty names, names over 255 characters and names with / are caught as you type; a taken name is caught when the server answers.

| Desktop | Mobile |
|---|---|
| ![Rename, desktop](openbox-wireframes/view-06-rename-desktop.svg) | ![Rename, mobile](openbox-wireframes/view-06-rename-mobile.svg) |

### Confirm delete

Delete always asks first and names the file. On mobile the same dialog fills the width.

| Desktop | Mobile |
|---|---|
| ![Confirm delete, desktop](openbox-wireframes/view-07-confirm-delete-desktop.svg) | ![Confirm delete, mobile](openbox-wireframes/view-07-confirm-delete-mobile.svg) |

### Sharing: file you can edit

Kate joined Q4 Budget.xls through a Can edit link. Files shared with you never show Share: only the owner can share a file. Both lists show the access you hold. Owners aren't named anywhere in the app.

| Desktop | Mobile |
|---|---|
| ![Sharing: file you can edit, desktop](openbox-wireframes/view-08-shared-can-edit-desktop.svg) | ![Sharing: file you can edit, mobile](openbox-wireframes/view-08-shared-can-edit-mobile.svg) |

### Sharing: view-only file

Kate can only view Brand guide.pdf.

| Desktop | Mobile |
|---|---|
| ![Sharing: view-only file, desktop](openbox-wireframes/view-09-shared-view-only-desktop.svg) | ![Sharing: view-only file, mobile](openbox-wireframes/view-09-shared-view-only-mobile.svg) |

### Share

Share shows only on files you own, and lists the file's links: there is no list of people. Each link shows what it gives, when it expires and how many people joined through it. Delete removes the link and everyone who joined through it.

| Desktop | Mobile |
|---|---|
| ![Share, desktop](openbox-wireframes/view-10-share-links-desktop.svg) | ![Share, mobile](openbox-wireframes/view-10-share-links-mobile.svg) |

### Create link

Pick what the link allows and when it expires: 1 day, 7 days or 30 days from now, never, or the end of a chosen day in your time zone. Days before today can't be picked. View can't be unticked. On mobile, the date opens the app's own calendar sheet.

| Desktop | Mobile |
|---|---|
| ![Create link, desktop](openbox-wireframes/view-11-create-link-desktop.svg) | ![Create link, mobile](openbox-wireframes/view-11-create-link-mobile.svg) |

### Link created

Done (× on mobile) closes it; the link then shows in Share, without its URL.

| Desktop | Mobile |
|---|---|
| ![Link created, desktop](openbox-wireframes/view-12-link-created-desktop.svg) | ![Link created, mobile](openbox-wireframes/view-12-link-created-mobile.svg) |

### Other confirmations

Replace, Remove my access and Delete link ask first too. On mobile each is the same dialog at full width. Delete a link names how many people still have access through it, and with none says only that it stops working.

| Desktop | Mobile |
|---|---|
| ![Other confirmations, desktop](openbox-wireframes/view-13-confirmations-desktop.svg) | ![Other confirmations, mobile](openbox-wireframes/view-13-confirmations-mobile.svg) |

### Search

Typing 2+ characters replaces the list with matching names from your files and files shared with you. Your access shows what you can do with each result: Full access on your own files. Budget 2027 draft.xlsx was shared with you, so it has no Share. Clearing the box goes back to the list you were in.

| Desktop | Mobile |
|---|---|
| ![Search, desktop](openbox-wireframes/view-14-search-desktop.svg) | ![Search, mobile](openbox-wireframes/view-14-search-mobile.svg) |

### Empty states

Every list has an empty state: My files, Shared with me, Shared by me, search and Share. Upload shows only in My files.

| Desktop | Mobile |
|---|---|
| ![Empty states, desktop](openbox-wireframes/view-15-empty-desktop.svg) | ![Empty states, mobile](openbox-wireframes/view-15-empty-mobile.svg) |

### Loading

Lists show placeholder rows until the first page arrives, and the Share dialog uses the same rows. Opening a share link shows the mobile page while it's redeemed; desktop shows the same in the page centre. A button that sends a request shows a spinner and ignores clicks until it answers. Scrolling to the end adds placeholder rows under the list; if that page fails, a Try again row replaces them, and after `invalid_after` the list reloads from the top.

| Desktop | Mobile |
|---|---|
| ![Loading, desktop](openbox-wireframes/view-16-loading-desktop.svg) | ![Loading, mobile](openbox-wireframes/view-16-loading-mobile.svg) |

### Page errors

A failed load offers Try again. A link that expired, was deleted or was never valid says why and offers a way out.

| Desktop | Mobile |
|---|---|
| ![Page errors, desktop](openbox-wireframes/view-17-errors-desktop.svg) | ![Page errors, mobile](openbox-wireframes/view-17-errors-mobile.svg) |

### Action and input errors

A failed action shows a toast naming the file, from its error message or the name the app already shows. Input errors show under the field. After a 401 the app signs in again and returns to the same page.

| Desktop | Mobile |
|---|---|
| ![Action and input errors, desktop](openbox-wireframes/view-18-action-errors-desktop.svg) | ![Action and input errors, mobile](openbox-wireframes/view-18-action-errors-mobile.svg) |

## 4. API

Base URL `https://<domain>/api/v1`. A single API instance serves every request, and there are no background jobs: all work happens inside the request that asks for it. Every request carries the session cookie set by sign-in.

Every response with a body is the same JSON envelope. `204 No Content` responses have no body.

```json
{
  "data": {},                             // the result; null when the request failed
  "errors": []                            // Error objects; [] on success
}
```

When a request fails, `data` is `null` and `errors` holds the error. `code` is the value listed in each endpoint's error table, for the app to branch on; `message` is a sentence the app can show as it is. A `422 validation_failed` lists one error per problem.

```http
HTTP/1.1 404 Not Found

{
  "data": null,
  "errors": [
    {                                     // Error
      "code": "not_found",
      "message": "File b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40 doesn't exist or you can't see it."
    }
  ]
}
```

### 4.1 Files

#### List files — `GET /files`

Lists one page of files for any list screen: My files, Shared with me, Shared by me, or search results. Pass at most one of `shared_with_me`, `shared_by_me`, `q`; with none, it lists your own files.

```http
GET /api/v1/files?shared_with_me=true&sort=name&order=asc&limit=50
```

| Parameter | Values |
|---|---|
| `shared_with_me` | `true`: files other people shared with you |
| `shared_by_me` | `true`: your files that someone else has access to |
| `q` | Name search, at least 2 characters. Matches your own files and files shared with you |
| `sort` | `name` (default) or `modified_at` |
| `order` | `asc` (default) or `desc` |
| `limit` | 1–200, default 50 |
| `after` | Id of the last file on the previous page; the next page starts right after it in the same `sort` and `order` |

```http
HTTP/1.1 200 OK

{
  "data": {
    "upload_policy": null,                // set only when listing your own files
    "items": [
      {                                         // File — the same object everywhere below
        "id": "b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40",
        "name": "Q4 Budget.xls",
        "owner_id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
        "mime_type": "application/vnd.ms-excel",
        "size_bytes": 183223,
        "access": "granted",                    // "owner" | "granted"
        "permissions": ["view", "edit"],        // what you may do
        "is_shared": true,                      // someone besides the owner has access
        "modified_at": "2026-03-17T09:33:00Z",
        "grants": [                             // [] unless it is shared with you
          {
            "link_id": "7b2e4d9a-1c8f-4a3e-b6d5-0f9c2a7e4b61",   // the link you joined through
            "permissions": ["view", "edit"],
            "granted_at": "2026-03-03T10:00:00Z"
          }
        ]
      }
    ],
    "has_more": false                     // true when another page follows
  },
  "errors": []
}
```

A file's `permissions` are all three on files you own, and what your links gave you on shared files. Rename and Share show only on files you own; Remove my access shows when `access` is `"granted"`. The Shared badge shows on files you own whose `is_shared` is true.

When listing your own files, `upload_policy` is:

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
| `422` | `validation_failed` | More than one filter, `q` shorter than 2 characters, or a bad `sort`, `order` or `limit` |
| `422` | `invalid_after` | `after` isn't a file in this list, e.g. it was deleted; reload from the start |

#### Rename — `POST /files/{id}/rename`

Renames a file and updates its `modified_at`. Only the owner can rename.

```http
POST /api/v1/files/f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68/rename

{ "name": "Staff review 2026.docx" }
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68",
    "name": "Staff review 2026.docx",
    "owner_id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "size_bytes": 48211,
    "access": "owner",
    "permissions": ["view", "edit", "delete"],
    "is_shared": true,
    "modified_at": "2026-11-05T09:41:00Z",
    "grants": []
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't own the file |
| `404` | `not_found` | The file doesn't exist or you can't see it |
| `409` | `name_conflict` | You already have a file with that name |
| `415` | `unsupported_file_type` | The new extension isn't allowed or doesn't match the file's type |
| `422` | `validation_failed` | Empty name, over 255 characters, or contains `/` |

#### Delete — `POST /files/{id}/delete`

Deletes a file permanently, for everyone, and removes its stored bytes. Needs `delete`.

```http
POST /api/v1/files/f7a2c9e4-1b6d-4f83-a0e5-7c4b2d9f1a68/delete
```

```http
HTTP/1.1 204 No Content
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't have `delete` |
| `404` | `not_found` | The file doesn't exist or you can't see it |

#### Remove my access — `POST /files/{id}/remove-access`

Removes a file shared with you from your list by deleting all your grants on it, The owner and everyone else keep their access.

```http
POST /api/v1/files/8e3b1f6d-2a9c-4d7e-b5f0-6c1a9d4e2b78/remove-access
```

```http
HTTP/1.1 204 No Content
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `404` | `not_found` | The file isn't shared with you |

#### Download — `POST /files/{id}/download`

Returns a signed storage URL, valid for 60 seconds, that saves the file under its real name. Needs `view`.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/download
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

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `404` | `not_found` | The file doesn't exist or you can't see it |

### 4.2 Uploads

#### Start upload — `POST /uploads`

Reserves a new file among your own files and returns where to send its bytes. Files are uploaded one at a time. The name stays reserved until the upload finishes or expires; starting the same name again replaces your own pending upload.

```http
POST /api/v1/uploads

{
  "name": "Q1 Budget.xlsx",
  "size_bytes": 201734,
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

```http
HTTP/1.1 201 Created

{
  "data": {                               // Upload — the same object everywhere below
    "id": "4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73",
    "name": "Q1 Budget.xlsx",
    "put_url": "https://store.blob.vercel-storage.com/uploads/4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73?token=8f2c1a9e5d3b",
    "put_headers": {
      "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    "expires_at": "2026-11-05T10:15:00Z"
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `409` | `name_conflict` | You already have a file with that name |
| `413` | `file_too_large` | Over 25 MB |
| `415` | `unsupported_file_type` | The extension isn't allowed or doesn't match `mime_type` |
| `422` | `validation_failed` | Empty name, over 255 characters, contains `/`, or a malformed body |

#### Replace contents — `POST /files/{id}/replace`

Starts an upload that replaces a file's contents. Finish it with `POST /uploads/{id}/complete`; the old contents are then deleted. Needs `edit`.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/replace

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
| `422` | `validation_failed` | Malformed body |

#### Finish upload — `POST /uploads/{id}/complete`

Call after the `PUT` succeeds. Confirms the bytes arrived, then makes the file visible. A replace upload returns the same file, with the same id.

```http
POST /api/v1/uploads/4c7b2e9f-8a3d-4b1c-a6e4-9f0d2c5b8e73/complete
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "91f0c6b3-5d2e-4a7f-b4c9-8e3a1d6f2b05",
    "name": "Q1 Budget.xlsx",
    "owner_id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "size_bytes": 201734,
    "access": "owner",
    "permissions": ["view", "edit", "delete"],
    "is_shared": false,
    "modified_at": "2026-11-05T10:02:00Z",
    "grants": []
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | For a replace, you no longer have `edit` |
| `404` | `not_found` | No such upload, it isn't yours, or the file it replaces was deleted |
| `409` | `upload_incomplete` | The bytes haven't arrived yet |
| `410` | `upload_expired` | The upload wasn't finished within 15 minutes; start again |

### 4.3 Links

Only a file's owner can list, create and delete its links. Anyone signed in can redeem one.

#### List links — `GET /files/{id}/links`

The file's links, newest first.

```http
GET /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/links
```

```http
HTTP/1.1 200 OK

{
  "data": [
    {                                     // Link — the same object everywhere below
      "id": "4f9c1a7e-6d2b-4e8a-9c3f-2b5d8e0a6c47",
      "permissions": ["view"],                // what the link gives
      "expires_at": "2026-11-12T22:59:59Z",   // null = never
      "redemption_count": 0,                  // people who joined through it
      "created_at": "2026-11-04T08:10:00Z"
    },
    {
      "id": "7b2e4d9a-1c8f-4a3e-b6d5-0f9c2a7e4b61",
      "permissions": ["view", "edit"],
      "expires_at": null,
      "redemption_count": 2,
      "created_at": "2026-03-02T14:20:00Z"
    },
    {
      "id": "d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31",
      "permissions": ["view"],
      "expires_at": "2026-12-05T22:59:59Z",
      "redemption_count": 3,
      "created_at": "2026-03-02T09:00:00Z"
    }
  ],
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't own the file |
| `404` | `not_found` | The file doesn't exist or you can't see it |

#### Create link — `POST /files/{id}/links`

Creates a share link. Anyone who opens it and signs in gets its permissions. For a chosen day the app sends the end of that day in the user's time zone; dates are shown in local time.

```http
POST /api/v1/files/b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40/links

{
  "permissions": ["view", "edit"],
  "expires_at": "2026-12-24T22:59:59Z"    // null = never
}
```

```http
HTTP/1.1 201 Created

{
  "data": {
    "id": "e5c1a8d3-7b2f-4e9a-8d6c-1f3b5a7e9c20",
    "url": "https://<domain>/links/7Fq9xKpL2mZr",   // only in this response
    "permissions": ["view", "edit"],              // what the link gives
    "expires_at": "2026-12-24T22:59:59Z",
    "redemption_count": 0,
    "created_at": "2026-11-05T10:05:00Z"
  },
  "errors": []
}
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't own the file |
| `404` | `not_found` | The file doesn't exist or you can't see it |
| `422` | `validation_failed` | `expires_at` is in the past, an unknown permission, or a set without `view` |

#### Delete link — `POST /links/{id}/delete`

The URL stops working and everyone who joined through it loses that access.

```http
POST /api/v1/links/d3a6f8b2-4c9e-4e1a-9b7d-6f2c0e8a5b31/delete
```

```http
HTTP/1.1 204 No Content
```

| Status | `code` | When |
|---|---|---|
| `401` | `unauthenticated` | No valid session |
| `403` | `forbidden` | You don't own the link's file |
| `404` | `not_found` | The link doesn't exist or you can't see it |

#### Redeem link — `POST /links/redeem`

Called by the web app's link page, `https://<domain>/links/{token}` (the URL people receive), after sign-in. Grants the link's permissions and returns the file, so the app can open Shared with me. Someone who already joined through another link gets this link's grant added. For the owner, or someone who still holds this link's grant, it returns the file and changes nothing, even after the link expires.

```http
POST /api/v1/links/redeem

{ "token": "7Fq9xKpL2mZr" }
```

```http
HTTP/1.1 200 OK

{
  "data": {
    "id": "b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40",
    "name": "Q4 Budget.xls",
    "owner_id": "3f6b1c2e-8d4a-4e71-9b2c-5a0f7d9e41c8",
    "mime_type": "application/vnd.ms-excel",
    "size_bytes": 190112,
    "access": "granted",
    "permissions": ["view", "edit"],
    "is_shared": true,
    "modified_at": "2026-11-05T10:06:00Z",
    "grants": [
      {
        "link_id": "e5c1a8d3-7b2f-4e9a-8d6c-1f3b5a7e9c20",
        "permissions": ["view", "edit"],
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
| `404` | `not_found` | The token doesn't match any link, or the link's file was deleted |
| `410` | `link_expired` | The link is past its `expires_at` |
| `410` | `link_deleted` | The link was deleted |
