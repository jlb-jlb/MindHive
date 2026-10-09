/*
 * MindHive Hidden Files
 * ---------------------
 * Hides chosen files and folders from the Obsidian file explorer, and puts an
 * eye button in the left ribbon to toggle them back into view.
 *
 * Three ways to match, all editable under Settings > MindHive Hidden Files:
 *
 *   prefixes  name starts with this   default "_"
 *   endings   name ends with this     default none
 *   names     full name matches       default index.md, log.md, CLAUDE.md,
 *                                             AGENTS.md, README.md
 *
 * The defaults clear the two kinds of clutter this vault produces. "_" marks
 * support material that is never opened directly, such as the "_attachments"
 * folder set as attachmentFolderPath in .obsidian/app.json. The named files are
 * the OKF scaffolding: an index.md and a log.md sit in every single directory,
 * and the agent instructions live at the root in two identical copies.
 *
 * How it works:
 *
 *  - One <style> element in document.head does all the hiding, rebuilt from the
 *    settings on every edit. The file explorer tags every row with data-path,
 *    so each matcher becomes an attribute selector on that path:
 *
 *      prefix P   [data-path^="P"]        vault root
 *                 [data-path*="/P"]       nested
 *      ending E   [data-path$="E"]        any depth, the path ends the same way
 *      name N     [data-path="N"]         vault root
 *                 [data-path$="/N"]       nested, the slash is what keeps
 *                                         "my-index.md" out of a match on
 *                                         "index.md"
 *
 *    Every selector carries the i flag, so a hand-typed "readme.md" still
 *    matches README.md, the way the Windows filesystem would.
 *
 *  - The primary rule hides the enclosing .tree-item, so a hidden folder takes
 *    its children with it instead of leaving an empty indent behind. The direct
 *    child combinator in :has(> .tree-item-self...) is what stops it from also
 *    matching every ancestor folder of a hidden note.
 *
 *  - The fallback rule repeats the match without :has(), because an unsupported
 *    selector invalidates the whole rule it appears in, and a fallback sharing
 *    that rule would go down with it.
 *
 *  - Both rules are scoped to the file explorer twice over, so hiding does not
 *    hinge on one attribute surviving an Obsidian update.
 *
 *  - Toggling flips styleEl.disabled rather than rebuilding, which stays
 *    instant on a large vault.
 *
 *  - Nothing is renamed, moved, or deleted. Links still resolve, attachments
 *    still render, search still finds these files, and the quick switcher still
 *    opens them. Only the explorer drawing changes.
 *
 *  - The ribbon icon shows the state: "eye-off" (the struck-through eye) while
 *    entries are hidden, "eye" while they are shown. State and settings live in
 *    data.json, so both survive a restart.
 *
 * NOTE: Obsidian caches plugin code. After editing this file, toggle the plugin
 * off and on under Settings > Community plugins, or restart Obsidian.
 */

const {
  Plugin,
  PluginSettingTab,
  Setting,
  setIcon,
  debounce,
} = require('obsidian');

const DEFAULTS = {
  hidden: true,
  prefixes: ['_'],
  endings: [],
  names: ['index.md', 'log.md', 'CLAUDE.md', 'AGENTS.md', 'README.md'],
};

// Two independent ways to name the file explorer, so the rules do not hinge on
// a single attribute surviving an Obsidian update. Both are explorer-only, so
// search results, bookmarks, and the quick switcher keep showing every file.
const SCOPES = [
  '.workspace-leaf-content[data-type="file-explorer"]',
  '.nav-files-container',
];

const clean = (list) =>
  (Array.isArray(list) ? list : []).map((v) => String(v).trim()).filter(Boolean);

const toLines = (list) => clean(list).join('\n');
const fromLines = (text) => clean(String(text).split('\n'));

// Attribute values are quoted, so a quote or a backslash typed into the
// settings would close the string early and break every rule after it.
const quote = (value) => value.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
const attr = (op, value) => `[data-path${op}"${quote(value)}" i]`;

function matchers(settings) {
  const found = [];

  for (const prefix of clean(settings.prefixes)) {
    found.push(attr('^=', prefix), attr('*=', `/${prefix}`));
  }

  for (const ending of clean(settings.endings)) {
    found.push(attr('$=', ending));
  }

  for (const name of clean(settings.names)) {
    found.push(attr('=', name), attr('$=', `/${name}`));
  }

  return found;
}

function buildCss(settings) {
  const found = matchers(settings);
  if (found.length === 0) {
    return '';
  }

  // Expands a selector shape across every scope and every matcher.
  const each = (fn) =>
    SCOPES.flatMap((scope) => found.map((m) => fn(scope, m))).join(',\n');

  return `
/* Primary: drop the whole tree item, so a folder takes its children along. */
${each((scope, m) => `${scope} .tree-item:has(> .tree-item-self${m})`)} {
  display: none;
}

/* Fallback for markup or engines without :has(), kept as its own rule so an
   unsupported selector above cannot take this one down with it. The sibling of
   a title row is its children container, whatever that container is called. */
${each((scope, m) => `${scope} ${m}`)},
${each((scope, m) => `${scope} ${m} + *`)} {
  display: none;
}
`;
}

module.exports = class HiddenFilesPlugin extends Plugin {
  async onload() {
    this.settings = Object.assign({}, DEFAULTS, await this.loadData());

    // Typing in a settings box repaints on every keystroke, which is cheap, and
    // writes to disk once the typing stops, which is not.
    this.saveSoon = debounce(() => this.saveData(this.settings), 500, true);

    this.styleEl = document.head.createEl('style', {
      attr: { id: 'mindhive-hidden-files' },
    });
    this.register(() => this.styleEl.remove());

    this.ribbonEl = this.addRibbonIcon('eye-off', 'Toggle hidden files', () =>
      this.toggle()
    );

    this.addCommand({
      id: 'toggle-hidden-files',
      name: 'Toggle hidden files',
      callback: () => this.toggle(),
    });

    this.addSettingTab(new HiddenFilesSettingTab(this.app, this));

    this.apply();
  }

  async toggle() {
    this.settings.hidden = !this.settings.hidden;
    this.apply();
    await this.saveData(this.settings);
  }

  // Rebuild the stylesheet and repaint the button. Run on load, on toggle, and
  // on every settings edit.
  apply() {
    this.styleEl.textContent = buildCss(this.settings);
    this.styleEl.disabled = !this.settings.hidden;

    this.ribbonEl.empty();
    setIcon(this.ribbonEl, this.settings.hidden ? 'eye-off' : 'eye');
    this.ribbonEl.setAttribute(
      'aria-label',
      this.settings.hidden ? 'Show hidden files' : 'Hide hidden files'
    );
  }
};

class HiddenFilesSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    this.containerEl.empty();

    this.addList(
      'Name prefixes',
      'Hidden when the name of a file or folder starts with one of these. A hidden folder takes its contents with it. One entry per line.',
      'prefixes',
      '_'
    );

    this.addList(
      'Name endings',
      'Hidden when the name ends with one of these, so a compound extension such as .excalidraw.md works here. One entry per line.',
      'endings',
      '.excalidraw.md'
    );

    this.addList(
      'Exact names',
      'Hidden when the whole name matches, in every folder of the vault. One entry per line.',
      'names',
      'index.md'
    );

    new Setting(this.containerEl)
      .setName('Restore defaults')
      .setDesc(
        `Back to the "_" prefix and the structural names: ${DEFAULTS.names.join(', ')}.`
      )
      .addButton((button) =>
        button.setButtonText('Restore').onClick(async () => {
          Object.assign(this.plugin.settings, {
            prefixes: DEFAULTS.prefixes.slice(),
            endings: DEFAULTS.endings.slice(),
            names: DEFAULTS.names.slice(),
          });
          this.plugin.apply();
          await this.plugin.saveData(this.plugin.settings);
          this.display();
        })
      );

    this.containerEl.createEl('p', {
      text: 'Matching ignores case, and nothing is renamed or moved. Hidden files still resolve through links, search, and the quick switcher.',
      cls: 'setting-item-description',
    });
  }

  addList(name, desc, key, placeholder) {
    const setting = new Setting(this.containerEl)
      .setName(name)
      .setDesc(desc)
      .addTextArea((area) => {
        area
          .setPlaceholder(placeholder)
          .setValue(toLines(this.plugin.settings[key]))
          .onChange((value) => {
            this.plugin.settings[key] = fromLines(value);
            this.plugin.apply();
            this.plugin.saveSoon();
          });

        area.inputEl.rows = 4;
        area.inputEl.style.width = '100%';
        area.inputEl.style.fontFamily = 'var(--font-monospace)';
      });

    setting.controlEl.style.flex = '1 1 18rem';
  }
}
