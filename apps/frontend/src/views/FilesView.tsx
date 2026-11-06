import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import './FilesView.css'

type Person = { id: string; display_name: string }
type FileItem = {
  id: string
  kind: 'file' | 'folder'
  name: string
  mime_type: string | null
  size_bytes: number | null
  access: 'owner' | 'granted' | 'path'
  permissions: string[]
  member_count: number
  modified_at: string | null
  modified_by: Person | null
}
type Folder = {
  id: string
  name: string
  path: { id: string; name: string }[]
  access: string
} | null
type Listing = {
  folder: Folder
  items: FileItem[]
  has_more: boolean
  upload_policy: { max_file_bytes: number; allowed_extensions: string[] } | null
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const formatDate = (value: string | null) =>
  value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: 'short', timeStyle: 'short' }).format(
        new Date(value),
      )
    : '—'
const formatSize = (bytes: number | null) =>
  bytes == null
    ? ''
    : bytes < 1024 * 1024
      ? `${Math.max(1, Math.round(bytes / 1024))} KB`
      : `${(bytes / 1024 / 1024).toFixed(1)} MB`
const extension = (name: string) => name.split('.').pop()?.toUpperCase().slice(0, 4) || 'FILE'

export default function FilesView() {
  const auth = useAuth()
  const token = auth.user?.access_token
  const [folderId, setFolderId] = useState<string | null>(null)
  const [listing, setListing] = useState<Listing>({
    folder: null,
    items: [],
    has_more: false,
    upload_policy: null,
  })
  const [selected, setSelected] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [dialog, setDialog] = useState<'folder' | 'rename' | 'delete' | null>(null)
  const [dialogValue, setDialogValue] = useState('')
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<'name' | 'modified_at'>('name')
  const [after, setAfter] = useState<string | null>(null)
  const uploadInput = useRef<HTMLInputElement>(null)

  const request = useCallback(
    async (path: string, init: RequestInit = {}) => {
      const response = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(init.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
          ...init.headers,
        },
      })
      const body = response.status === 204 ? null : await response.json().catch(() => null)
      if (!response.ok)
        throw new Error(
          body?.errors?.[0]?.message || body?.message || `Request failed (${response.status})`,
        )
      return body
    },
    [token],
  )

  const load = useCallback(
    async (id = folderId, append = false, cursor: string | null = null) => {
      if (!token) return
      setLoading(true)
      setError('')
      try {
        const params = new URLSearchParams({ sort, order: 'asc', limit: '50' })
        if (search.trim().length >= 2) params.set('q', search.trim())
        else if (id) params.set('folder_id', id)
        if (cursor) params.set('after', cursor)
        const result = await request(`/files?${params}`)
        const data = result.data
        setListing((old) => ({
          folder: data.folder,
          items: append ? [...old.items, ...data.items] : data.items,
          has_more: data.has_more,
          upload_policy: data.upload_policy,
        }))
        setAfter(data.items.at(-1)?.id || null)
        if (!append) setSelected([])
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Could not load files.')
      } finally {
        setLoading(false)
      }
    },
    [token, folderId, sort, search, request],
  )

  useEffect(() => {
    void load(folderId)
  }, [folderId, sort, search, load])

  const selectedItems = useMemo(
    () => listing.items.filter((item) => selected.includes(item.id)),
    [listing.items, selected],
  )
  const allSelected =
    listing.items.length > 0 && listing.items.every((item) => selected.includes(item.id))
  const toggle = (id: string) =>
    setSelected((current) =>
      current.includes(id) ? current.filter((x) => x !== id) : [...current, id],
    )
  const openFolder = (item: FileItem) => {
    if (item.kind === 'folder') setFolderId(item.id)
    else toggle(item.id)
  }
  const goUp = (id: string | null) => setFolderId(id)

  const createFolder = async () => {
    if (!dialogValue.trim()) return
    setBusy(true)
    try {
      await request('/files/folders', {
        method: 'POST',
        body: JSON.stringify({ folder_id: folderId, name: dialogValue.trim() }),
      })
      setDialog(null)
      setDialogValue('')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not create folder.')
    } finally {
      setBusy(false)
    }
  }
  const renameSelected = async () => {
    if (selectedItems.length !== 1 || !dialogValue.trim()) return
    setBusy(true)
    try {
      await request(`/files/${selectedItems[0].id}/rename`, {
        method: 'POST',
        body: JSON.stringify({ name: dialogValue.trim() }),
      })
      setDialog(null)
      setDialogValue('')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not rename item.')
    } finally {
      setBusy(false)
    }
  }
  const deleteSelected = async () => {
    setBusy(true)
    try {
      await request('/files/delete', { method: 'POST', body: JSON.stringify({ ids: selected }) })
      setDialog(null)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not delete items.')
    } finally {
      setBusy(false)
    }
  }
  const downloadSelected = async () => {
    setBusy(true)
    try {
      const result = await request('/files/download', {
        method: 'POST',
        body: JSON.stringify({ ids: selected }),
      })
      const downloads = Array.isArray(result.data) ? result.data : [result.data]
      downloads.forEach((entry: { url: string }) => {
        const a = document.createElement('a')
        a.href = entry.url
        a.target = '_blank'
        a.rel = 'noreferrer'
        a.click()
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not download selection.')
    } finally {
      setBusy(false)
    }
  }
  const uploadFiles = async (files: FileList | null) => {
    if (!files?.length) return
    setBusy(true)
    setError('')
    try {
      const fileArray = Array.from(files)
      const started = await request('/uploads', {
        method: 'POST',
        body: JSON.stringify({
          folder_id: folderId,
          files: fileArray.map((file) => ({
            name: file.name,
            size_bytes: file.size,
            mime_type: file.type || 'application/octet-stream',
          })),
        }),
      })
      for (const upload of started.data || []) {
        const file = fileArray.find((f) => f.name === upload.name)
        if (!file) continue
        const put = await fetch(upload.put_url, {
          method: 'PUT',
          headers: upload.put_headers || {},
          body: file,
        })
        if (!put.ok) throw new Error(`Upload failed for ${file.name}`)
        await request(`/uploads/${upload.id}/complete`, { method: 'POST' })
      }
      if (started.errors?.length)
        setError(started.errors.map((x: { message: string }) => x.message).join(' '))
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed.')
    } finally {
      setBusy(false)
      if (uploadInput.current) uploadInput.current.value = ''
    }
  }

  if (auth.isLoading) return <main className="files-state">Loading OpenBox…</main>
  if (!auth.isAuthenticated)
    return (
      <main className="files-state">
        Please sign in to view your files. <a href="/signin">Sign in</a>
      </main>
    )

  return (
    <main className="files-app">
      <header className="files-topbar">
        <a className="files-brand" href="/">
          OpenBox
        </a>
        <nav className="files-primary-nav">
          <a className="is-active" href="/files">
            Files
          </a>
          <a href="/sharing">Sharing</a>
        </nav>
        <div className="files-topbar__right">
          <label className="files-search">
            <span aria-hidden="true">⌕</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search"
              aria-label="Search files"
            />
          </label>
          <button className="files-avatar" aria-label="Account">
            {auth.user?.profile?.name
              ?.toString()
              .split(' ')
              .map((x) => x[0])
              .join('')
              .slice(0, 2) || 'AL'}
          </button>
        </div>
      </header>
      <section className="files-content">
        <div className="files-heading-row">
          <div className="files-breadcrumbs">
            <button onClick={() => goUp(null)}>My files</button>
            {listing.folder?.path.map((part) => (
              <span key={part.id}>
                <span className="crumb-separator">›</span>
                <button onClick={() => goUp(part.id)}>{part.name}</button>
              </span>
            ))}
            {listing.folder && (
              <>
                <span className="crumb-separator">›</span>
                <strong>{listing.folder.name}</strong>
              </>
            )}
          </div>
          <div className="files-heading-actions">
            <button
              className="files-btn files-btn--secondary"
              onClick={() => {
                setDialogValue('')
                setDialog('folder')
              }}
            >
              ＋ New folder
            </button>
            <button
              className="files-btn files-btn--primary"
              onClick={() => uploadInput.current?.click()}
              disabled={!listing.upload_policy}
            >
              ↑ Upload
            </button>
            <input
              ref={uploadInput}
              type="file"
              multiple
              hidden
              onChange={(e) => void uploadFiles(e.target.files)}
            />
          </div>
        </div>
        {error && (
          <div className="files-alert" role="alert">
            {error}
            <button onClick={() => setError('')} aria-label="Dismiss">
              ×
            </button>
          </div>
        )}
        <div className="files-table-wrap">
          <table className="files-table">
            <thead>
              <tr>
                <th className="check-col">
                  <input
                    type="checkbox"
                    aria-label="Select all"
                    checked={allSelected}
                    onChange={() =>
                      setSelected(allSelected ? [] : listing.items.map((item) => item.id))
                    }
                  />
                </th>
                <th>
                  <button
                    className="sort-button"
                    onClick={() => setSort(sort === 'name' ? 'modified_at' : 'name')}
                  >
                    Name <span>⌄</span>
                  </button>
                </th>
                <th>Modified</th>
                <th>Members</th>
              </tr>
            </thead>
            <tbody>
              {loading && !listing.items.length ? (
                <tr>
                  <td colSpan={4} className="files-empty">
                    Loading files…
                  </td>
                </tr>
              ) : listing.items.length === 0 ? (
                <tr>
                  <td colSpan={4} className="files-empty">
                    {search ? 'No matching files or folders.' : 'This folder is empty.'}
                  </td>
                </tr>
              ) : (
                listing.items.map((item) => (
                  <tr
                    key={item.id}
                    className={selected.includes(item.id) ? 'is-selected' : ''}
                    onDoubleClick={() => openFolder(item)}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={selected.includes(item.id)}
                        onChange={() => toggle(item.id)}
                        aria-label={`Select ${item.name}`}
                      />
                    </td>
                    <td>
                      <div className="file-name-cell">
                        <span
                          className={`file-type ${item.kind === 'folder' ? 'file-type--folder' : ''}`}
                        >
                          {item.kind === 'folder' ? '▰' : extension(item.name)}
                        </span>
                        <button className="file-name" onClick={() => openFolder(item)}>
                          {item.name}
                        </button>
                      </div>
                    </td>
                    <td className="modified-cell">
                      {item.modified_at ? (
                        <>
                          <span>{formatDate(item.modified_at)}</span>
                          <small>by {item.modified_by?.display_name || '—'}</small>
                        </>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="members-cell">
                      {item.member_count} {item.member_count === 1 ? 'member' : 'members'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {listing.has_more && (
          <button
            className="files-load-more"
            disabled={loading || !after}
            onClick={() => void load(folderId, true, after)}
          >
            Load more
          </button>
        )}
      </section>
      {selectedItems.length > 0 && (
        <div className="files-selection-toolbar">
          <button
            className="toolbar-clear"
            onClick={() => setSelected([])}
            aria-label="Clear selection"
          >
            ×
          </button>
          <strong>{selectedItems.length} selected</strong>
          {selectedItems.every((x) => x.permissions.includes('view')) &&
            !selectedItems.some((x) => x.kind === 'folder' && x.access === 'path') && (
              <button onClick={() => void downloadSelected()}>↓ Download</button>
            )}
          {selectedItems.length === 1 && selectedItems[0].permissions.includes('rename') && (
            <button
              onClick={() => {
                setDialogValue(selectedItems[0].name)
                setDialog('rename')
              }}
            >
              ✎ Rename
            </button>
          )}
          {selectedItems.every((x) => x.permissions.includes('delete')) && (
            <button className="toolbar-delete" onClick={() => setDialog('delete')}>
              ▤ Delete
            </button>
          )}
        </div>
      )}
      {dialog && (
        <div className="files-modal-backdrop" role="presentation">
          <section
            className="files-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="files-modal-title"
          >
            <h2 id="files-modal-title">
              {dialog === 'folder'
                ? 'Create a folder'
                : dialog === 'rename'
                  ? 'Rename item'
                  : 'Delete selected items?'}
            </h2>
            {dialog === 'delete' ? (
              <p>This permanently deletes the selected items for everyone who has access.</p>
            ) : (
              <input
                autoFocus
                value={dialogValue}
                onChange={(e) => setDialogValue(e.target.value)}
                placeholder="Folder name"
                maxLength={255}
                onKeyDown={(e) => {
                  if (e.key === 'Enter')
                    void (dialog === 'folder' ? createFolder() : renameSelected())
                }}
              />
            )}
            <div className="files-modal-actions">
              <button className="files-btn files-btn--secondary" onClick={() => setDialog(null)}>
                Cancel
              </button>
              <button
                className={`files-btn ${dialog === 'delete' ? 'files-btn--danger' : 'files-btn--primary'}`}
                disabled={busy || (dialog !== 'delete' && !dialogValue.trim())}
                onClick={() =>
                  void (dialog === 'folder'
                    ? createFolder()
                    : dialog === 'rename'
                      ? renameSelected()
                      : deleteSelected())
                }
              >
                {busy ? 'Working…' : dialog === 'delete' ? 'Delete' : 'Save'}
              </button>
            </div>
          </section>
        </div>
      )}
      <nav className="files-mobile-tabs">
        <a className="is-active" href="/files">
          ▣<span>Files</span>
        </a>
        <a href="/sharing">
          ♧<span>Sharing</span>
        </a>
      </nav>
      {busy && (
        <div className="files-busy" aria-live="polite">
          Working…
        </div>
      )}
    </main>
  )
}
