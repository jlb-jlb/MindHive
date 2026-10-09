/*
 * MindHive HTML View
 * ------------------
 * Renders local .html files inside an Obsidian tab, with their CSS and
 * JavaScript fully active.
 *
 * How it works:
 *
 *  - registerExtensions(['html', 'htm']) claims those files for this view,
 *    so clicking one in the file explorer opens it like a note.
 *
 *  - The view mounts a borderless <iframe> whose src is the vault-local
 *    resource URL (app://...), so the page renders from its real location
 *    on disk, and re-sets that src when the file is modified, which gives
 *    live feedback while editing the HTML in a split pane.
 *
 *  - Message bridge. Embedded pages must NOT construct vault URLs
 *    themselves: relative resolution inside app:// documents is
 *    unreliable (on Windows the URL carries encoded backslashes), and
 *    even a correctly shaped resource URL is not guaranteed to load from
 *    inside the frame. So the page asks, and this plugin answers using
 *    Obsidian's own APIs. Image bytes are handed over directly rather
 *    than as a URL, which is the only approach immune to all of the
 *    above. All paths are vault-relative. Protocol:
 *
 *      page -> plugin
 *      { type: 'mindhive-ping', id }
 *          replies { id, ok, version } — handshake, also proves to the
 *          page that a current build of this plugin is loaded
 *      { type: 'mindhive-open', path }
 *          opens the note in a new tab via workspace.openLinkText
 *      { type: 'mindhive-read', id, path }
 *          replies { id, ok, text | error }        (adapter.read)
 *      { type: 'mindhive-list', id, path }
 *          replies { id, ok, files, folders | error } (adapter.list),
 *          so a page can walk the real folder tree instead of trusting
 *          generated index files to be current
 *      { type: 'mindhive-image', id, path }
 *          replies { id, ok, buffer, mime | error } (adapter.readBinary);
 *          the page wraps the buffer in a Blob and uses an object URL
 *      { type: 'mindhive-resource', id, path }
 *          replies { id, ok, url | error }          (getResourcePath),
 *          kept as a lighter-weight alternative to mindhive-image
 *
 *      plugin -> page
 *      { type: 'mindhive-vault-changed', event, path, oldPath }
 *          sent into every open HTML view when any vault file is
 *          modified, created, deleted, or renamed (except the view's own
 *          file, which reloads instead). Live dashboards use this to
 *          re-read their data the moment a note changes.
 *
 *    Replies go to evt.source, so several HTML views can coexist. The
 *    bridge is read-only apart from 'open', and this is a personal, local
 *    vault, so no origin filtering is applied.
 *
 *  NOTE: Obsidian caches plugin code. After editing this file, toggle the
 *  plugin off and on under Settings > Community plugins (or restart
 *  Obsidian); reopening the HTML file is not enough. PLUGIN_VERSION below
 *  is what a page sees via mindhive-ping, so a stale build is detectable.
 */

const { Plugin, FileView, normalizePath } = require('obsidian');

const VIEW_TYPE = 'mindhive-html-view';
const PLUGIN_VERSION = '1.4.0';

const MIME_BY_EXT = {
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  png: 'image/png',
  gif: 'image/gif',
  webp: 'image/webp',
  avif: 'image/avif',
  svg: 'image/svg+xml',
  bmp: 'image/bmp',
};

function mimeFor(path) {
  const ext = path.split('.').pop().toLowerCase();
  return MIME_BY_EXT[ext] || 'application/octet-stream';
}

class HtmlFileView extends FileView {
  getViewType() {
    return VIEW_TYPE;
  }

  getDisplayText() {
    return this.file ? this.file.basename : 'HTML';
  }

  getIcon() {
    return 'layout-dashboard';
  }

  canAcceptExtension(extension) {
    return extension === 'html' || extension === 'htm';
  }

  async onOpen() {
    // The frame owns all scrolling and spacing; the view chrome stays flush.
    this.contentEl.setAttr('style', 'padding:0;overflow:hidden;');

    // The open file itself reloads on save; every other vault change is
    // forwarded into the page so live dashboards can refresh.
    const forward = (event) => (file, oldPath) => {
      if (this.file && file && file.path === this.file.path) {
        if (event === 'modify') this.render();
        return;
      }
      const w = this._frame && this._frame.contentWindow;
      if (w) {
        w.postMessage(
          {
            type: 'mindhive-vault-changed',
            event,
            path: file ? file.path : '',
            oldPath: oldPath || '',
          },
          '*'
        );
      }
    };
    for (const event of ['modify', 'create', 'delete', 'rename']) {
      this.registerEvent(this.app.vault.on(event, forward(event)));
    }
  }

  async onLoadFile(file) {
    this.render(file);
  }

  async onUnloadFile() {
    this._frame = null;
    this.contentEl.empty();
  }

  render(file = this.file) {
    if (!file) return;
    this.contentEl.empty();
    const frame = this.contentEl.createEl('iframe');
    frame.setAttr(
      'style',
      'width:100%;height:100%;border:0;display:block;background:transparent;'
    );
    frame.src = this.app.vault.adapter.getResourcePath(file.path);
    this._frame = frame;
  }
}

module.exports = class MindHiveHtmlViewPlugin extends Plugin {
  onload() {
    this.registerView(VIEW_TYPE, (leaf) => new HtmlFileView(leaf));
    this.registerExtensions(['html', 'htm'], VIEW_TYPE);

    const onMessage = (evt) => {
      const d = evt && evt.data;
      if (!d || typeof d.type !== 'string') return;
      const reply = (payload) => {
        if (evt.source && typeof evt.source.postMessage === 'function') {
          evt.source.postMessage(payload, '*');
        }
      };

      if (d.type === 'mindhive-ping') {
        reply({ id: d.id, ok: true, version: PLUGIN_VERSION });
        return;
      }

      if (d.type === 'mindhive-open' && typeof d.path === 'string') {
        this.app.workspace.openLinkText(d.path, '', 'tab');
        return;
      }

      if (d.type === 'mindhive-read' && typeof d.path === 'string') {
        this.app.vault.adapter
          .read(normalizePath(d.path))
          .then((text) => reply({ id: d.id, ok: true, text }))
          .catch((err) => reply({ id: d.id, ok: false, error: String(err) }));
        return;
      }

      if (d.type === 'mindhive-list' && typeof d.path === 'string') {
        this.app.vault.adapter
          .list(normalizePath(d.path))
          .then((res) =>
            reply({
              id: d.id,
              ok: true,
              files: res.files || [],
              folders: res.folders || [],
            })
          )
          .catch((err) => reply({ id: d.id, ok: false, error: String(err) }));
        return;
      }

      if (d.type === 'mindhive-image' && typeof d.path === 'string') {
        this.app.vault.adapter
          .readBinary(normalizePath(d.path))
          .then((buffer) =>
            reply({ id: d.id, ok: true, buffer, mime: mimeFor(d.path) })
          )
          .catch((err) => reply({ id: d.id, ok: false, error: String(err) }));
        return;
      }

      if (d.type === 'mindhive-resource' && typeof d.path === 'string') {
        try {
          reply({
            id: d.id,
            ok: true,
            url: this.app.vault.adapter.getResourcePath(normalizePath(d.path)),
          });
        } catch (err) {
          reply({ id: d.id, ok: false, error: String(err) });
        }
      }
    };

    window.addEventListener('message', onMessage);
    this.register(() => window.removeEventListener('message', onMessage));
  }
};
