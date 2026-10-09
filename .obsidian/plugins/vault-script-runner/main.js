const { Modal, Notice, Plugin, PluginSettingTab, Setting, requestUrl } = require("obsidian");
const { spawn } = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { fileURLToPath } = require("url");

const DEFAULT_SETTINGS = {
  pythonExecutable: "",
  defaultVenvPath: "{{pluginDir}}/.venv",
  downloadsDir: "",
  scriptCatalogUrl: "https://raw.githubusercontent.com/jlb-jlb/vault-script-runner/main/catalog/catalog.json",
  installedScripts: {},
  scripts: [],
};

module.exports = class VaultScriptRunnerPlugin extends Plugin {
  async onload() {
    this.scriptCommandIds = new Set();
    await this.loadSettings();

    this.addRibbonIcon("terminal", "Run script", () => this.openScriptPicker());

    this.addCommand({
      id: "run-configured-script",
      name: "Run configured script",
      callback: () => this.openScriptPicker(),
    });

    this.addCommand({
      id: "refresh-script-catalog",
      name: "Refresh script catalog",
      callback: async () => {
        try {
          await this.fetchScriptCatalog();
          new Notice("Script catalog refreshed.");
        } catch (error) {
          new Notice(`Could not refresh script catalog: ${error.message}`, 10000);
        }
      },
    });

    this.addSettingTab(new VaultScriptRunnerSettingTab(this.app, this));
    this.refreshScriptCommands();
  }

  async loadSettings() {
    const loaded = await this.loadData();
    const data = loaded && typeof loaded === "object" ? loaded : {};
    this.settings = {
      ...DEFAULT_SETTINGS,
      ...data,
      installedScripts: data.installedScripts && typeof data.installedScripts === "object" ? data.installedScripts : {},
      scripts: Array.isArray(data.scripts) ? data.scripts.map((script) => normalizeScript(script)) : [],
    };
  }

  async saveSettings() {
    await this.saveData(this.settings);
    if (this.scriptCommandIds) {
      this.refreshScriptCommands();
    }
  }

  getVaultBasePath() {
    const adapter = this.app.vault.adapter;
    if (adapter && typeof adapter.getBasePath === "function") {
      return adapter.getBasePath();
    }
    if (adapter && typeof adapter.basePath === "string") {
      return adapter.basePath;
    }
    return "";
  }

  getPluginDir() {
    const vaultPath = this.getVaultBasePath();
    return vaultPath ? path.join(vaultPath, ".obsidian", "plugins", this.manifest.id) : "";
  }

  getScriptsDir() {
    return path.join(this.getPluginDir(), "scripts");
  }

  getDownloadsDir() {
    const override = String(this.settings.downloadsDir || "").trim();
    if (override) {
      const home = os.homedir();
      const rendered = stripWrappingQuotes(
        this.renderTemplate(override, {
          vault: this.getVaultBasePath(),
          pluginDir: this.getPluginDir(),
          home,
        }).trim()
      );
      const expanded = rendered.replace(/^~(?=[\\/]|$)/, home);
      if (expanded) {
        return path.isAbsolute(expanded) ? expanded : path.join(this.getVaultBasePath() || home, expanded);
      }
    }
    return resolveDownloadsDir();
  }

  getScripts() {
    return Array.isArray(this.settings.scripts)
      ? this.settings.scripts.filter((script) => script && script.name && script.command)
      : [];
  }

  refreshScriptCommands() {
    if (!this.scriptCommandIds) {
      this.scriptCommandIds = new Set();
    }

    for (const commandId of this.scriptCommandIds) {
      this.removeCommandById(commandId);
    }
    this.scriptCommandIds.clear();

    const usedIds = new Set(["run-configured-script", "refresh-script-catalog"]);
    this.getScripts().forEach((script, index) => {
      const commandId = uniqueCommandId(`run-script-${script.id || script.name || index + 1}`, usedIds);
      usedIds.add(commandId);
      this.scriptCommandIds.add(commandId);
      this.addCommand({
        id: commandId,
        name: `Run ${script.name}`,
        callback: () => {
          const currentScript = this.getScripts().find((candidate) => candidate.id === script.id) || script;
          this.openRunModal(currentScript);
        },
      });
    });
  }

  removeCommandById(commandId) {
    // Obsidian exposes no public API for removing a command at runtime, which is
    // needed to refresh the per-script palette entries when presets change.
    // removeCommand is the narrowest available call; guard it so a future API
    // change degrades gracefully instead of throwing.
    const commands = this.app.commands;
    const fullId = `${this.manifest.id}:${commandId}`;
    if (commands && typeof commands.removeCommand === "function") {
      commands.removeCommand(fullId);
    }
  }

  openScriptPicker() {
    const scripts = this.getScripts();
    if (scripts.length === 0) {
      new Notice("Vault Script Runner: no scripts configured.");
      return;
    }
    if (scripts.length === 1) {
      this.openRunModal(scripts[0]);
      return;
    }
    new ScriptPickerModal(this.app, this, scripts).open();
  }

  openRunModal(script) {
    new ScriptRunModal(this.app, this, script).open();
  }

  async fetchScriptCatalog() {
    const variables = this.buildVariables({});
    const catalogUrl = stripWrappingQuotes(this.renderTemplate(this.settings.scriptCatalogUrl || "", variables).trim());
    if (!catalogUrl) {
      throw new Error("Script catalog URL is empty.");
    }

    const text = await readTextLocation(catalogUrl, this.getPluginDir());
    const catalog = JSON.parse(text);
    if (!catalog || !Array.isArray(catalog.scripts)) {
      throw new Error("Script catalog must contain a scripts array.");
    }

    this.scriptCatalog = {
      ...catalog,
      url: catalogUrl,
      scripts: catalog.scripts.map((entry) => normalizeCatalogEntry(entry)).filter(Boolean),
    };
    this.scriptCatalogError = "";
    return this.scriptCatalog;
  }

  getCatalogScriptPath(entry) {
    return path.join(this.getScriptsDir(), safeScriptFileName(entry.fileName || `${entry.id}.py`));
  }

  getCatalogScriptUrl(entry) {
    const catalogUrl = this.scriptCatalog?.url || this.renderTemplate(this.settings.scriptCatalogUrl || "", this.buildVariables({}));
    return resolveLocation(entry.url || entry.path || entry.fileName, catalogUrl);
  }

  getCatalogInstallState(entry) {
    const installed = this.settings.installedScripts?.[entry.id] || null;
    const scriptPath = this.getCatalogScriptPath(entry);
    if (!installed) {
      return { status: "download", installed, scriptPath };
    }
    // If the install record survived but its preset is gone (e.g. the preset
    // was removed in an older version), offer the script for download again so
    // re-downloading restores a usable preset instead of leaving a dead record.
    const hasPreset = (this.settings.scripts || []).some((script) => script.catalogScriptId === entry.id);
    if (!hasPreset) {
      return { status: "download", installed, scriptPath };
    }
    if (compareVersions(entry.version || "0.0.0", installed.version || "0.0.0") > 0) {
      return { status: "update", installed, scriptPath };
    }
    if (!fs.existsSync(scriptPath)) {
      return { status: "download", installed, scriptPath };
    }
    return { status: "installed", installed, scriptPath };
  }

  async installCatalogScript(entry) {
    const scriptUrl = this.getCatalogScriptUrl(entry);
    const content = await readTextLocation(scriptUrl, this.getPluginDir());
    const actualHash = sha256(content);
    if (entry.sha256 && actualHash.toLowerCase() !== String(entry.sha256).toLowerCase()) {
      throw new Error(`Hash mismatch. Expected ${entry.sha256}, got ${actualHash}.`);
    }

    const targetPath = this.getCatalogScriptPath(entry);
    fs.mkdirSync(path.dirname(targetPath), { recursive: true });
    fs.writeFileSync(targetPath, content, "utf8");

    this.settings.installedScripts = {
      ...(this.settings.installedScripts || {}),
      [entry.id]: {
        id: entry.id,
        name: entry.name,
        version: entry.version || "0.0.0",
        fileName: path.basename(targetPath),
        sourceUrl: scriptUrl,
        installedAt: new Date().toISOString(),
        sha256: entry.sha256 || actualHash,
      },
    };

    if (entry.preset) {
      const preset = normalizeScript({
        ...entry.preset,
        catalogScriptId: entry.id,
      });
      upsertScriptPreset(this.settings.scripts, preset);
    }

    await this.saveSettings();
  }

  buildVariables(parameterValues = {}, script = null) {
    const vaultPath = this.getVaultBasePath();
    const pluginDir = this.getPluginDir();
    const scriptsDir = this.getScriptsDir();
    const activeFile = this.app.workspace.getActiveFile();
    const activeFilePath = activeFile ? activeFile.path : "";
    const activeFolder = normalizeObsidianFolder(activeFile && activeFile.parent ? activeFile.parent.path : "");
    const activeFolderPrefix = activeFolder ? `${activeFolder}/` : "";
    const downloadsPath = this.getDownloadsDir();
    const latestDownload = findLatestFile(downloadsPath);
    const latestDownloadPdf = findLatestFile(downloadsPath, ".pdf");
    const now = new Date();

    const variables = {
      vault: vaultPath,
      pluginDir,
      scriptsDir,
      downloads: downloadsPath,
      latestDownload,
      latestDownloadPdf,
      activeFile: activeFilePath,
      activeFolder,
      activeFolderPrefix,
      date: formatDate(now),
      time: formatTime(now),
    };

    if (script && script.catalogScriptId) {
      const installed = this.settings.installedScripts?.[script.catalogScriptId];
      const scriptPath = installed ? path.join(scriptsDir, installed.fileName) : "";
      variables.scriptPath = scriptPath;
      variables.scriptDir = scriptPath ? path.dirname(scriptPath) : scriptsDir;
      variables.scriptVersion = installed?.version || "";
      addPathVariables(variables, "scriptPath", scriptPath);
      addPathVariables(variables, "scriptDir", variables.scriptDir);
    }

    addPathVariables(variables, "activeFile", activeFilePath);
    addPathVariables(variables, "activeFolder", activeFolder);
    addPathVariables(variables, "downloads", downloadsPath);
    addPathVariables(variables, "latestDownload", latestDownload);
    addPathVariables(variables, "latestDownloadPdf", latestDownloadPdf);
    addPathVariables(variables, "pluginDir", pluginDir);
    addPathVariables(variables, "scriptsDir", scriptsDir);

    for (const [key, value] of Object.entries(parameterValues)) {
      variables[key] = value;
      addPathVariables(variables, key, value);
    }

    return variables;
  }

  addVenvVariables(script, variables) {
    const vaultPath = variables.vault || this.getVaultBasePath();
    const sharedTemplate = this.settings.defaultVenvPath || "{{pluginDir}}/.venv";
    let sharedVenvPath = stripWrappingQuotes(this.renderTemplate(sharedTemplate, variables).trim());
    if (sharedVenvPath && !path.isAbsolute(sharedVenvPath)) {
      sharedVenvPath = path.join(vaultPath, sharedVenvPath);
    }

    variables.sharedVenvPath = sharedVenvPath;
    variables.sharedVenvPython = sharedVenvPath ? getVenvPythonPath(sharedVenvPath) : "";
    addPathVariables(variables, "sharedVenvPath", sharedVenvPath);
    addPathVariables(variables, "sharedVenvPython", variables.sharedVenvPython);

    const venvTemplate = script.venvPath || "{{sharedVenvPath}}";
    let venvPath = stripWrappingQuotes(this.renderTemplate(venvTemplate, variables).trim());
    if (venvPath && !path.isAbsolute(venvPath)) {
      venvPath = path.join(vaultPath, venvPath);
    }

    variables.venvPath = venvPath;
    variables.venvPython = venvPath ? getVenvPythonPath(venvPath) : "";
    addPathVariables(variables, "venvPath", venvPath);
    addPathVariables(variables, "venvPython", variables.venvPython);

    return { venvPath, venvPython: variables.venvPython };
  }

  renderTemplate(value, variables) {
    return String(value || "").replace(/\{\{\s*([A-Za-z0-9_.:-]+)\s*\}\}/g, (_match, key) => {
      if (Object.prototype.hasOwnProperty.call(variables, key)) {
        return variables[key] == null ? "" : String(variables[key]);
      }
      return "";
    });
  }

  async ensureVenv(script, variables, cwd, env, setupLogs) {
    if (!script.useVenv) {
      return;
    }

    const { venvPath, venvPython } = this.addVenvVariables(script, variables);
    if (!venvPath || !venvPython) {
      throw new Error("Virtual environment path is empty.");
    }

    if (!fs.existsSync(venvPython)) {
      const configured = stripWrappingQuotes(
        this.renderTemplate(script.pythonExecutable || this.settings.pythonExecutable || "", variables).trim()
      );
      // Try the configured interpreter first, then OS-appropriate fallbacks, so a
      // fresh machine works whether the interpreter is `python`, `python3`, or `py`.
      const fallbacks = process.platform === "win32" ? ["python", "py", "python3"] : ["python3", "python"];
      const candidates = [configured, ...fallbacks].filter(
        (name, index, all) => name && all.indexOf(name) === index
      );

      fs.mkdirSync(path.dirname(venvPath), { recursive: true });
      new Notice(`Creating virtual environment for ${script.name}`);

      let createResult = null;
      const tried = [];
      for (const creator of candidates) {
        createResult = await runProcess(creator, ["-m", "venv", venvPath], { cwd, env, shell: false });
        setupLogs.push({ label: `create virtual environment (${creator})`, result: createResult });
        tried.push(creator);
        if (createResult.code === 0 && fs.existsSync(venvPython)) {
          break;
        }
      }
      if (!createResult || createResult.code !== 0 || !fs.existsSync(venvPython)) {
        throw new Error(
          `Could not create virtual environment. Tried interpreter(s): ${tried.join(", ")}. ` +
            "Set a working Python interpreter under Vault Script Runner settings.\n" +
            (createResult?.stderr || createResult?.stdout || "")
        );
      }
    }

    const requirements = normalizeRequirementText(script.requirements);
    if (!requirements) {
      return;
    }

    const key = slugify(script.id || script.name || "script");
    const markerPath = path.join(venvPath, `.vault-script-runner-requirements.${key}.txt`);
    const requirementsPath = path.join(venvPath, `.vault-script-runner-requirements.${key}.in`);
    if (readTextIfExists(markerPath) === requirements) {
      return;
    }

    fs.writeFileSync(requirementsPath, `${requirements}\n`, "utf8");
    new Notice(`Installing requirements for ${script.name}`);
    const installResult = await runProcess(venvPython, ["-m", "pip", "install", "-r", requirementsPath], {
      cwd,
      env,
      shell: false,
    });
    setupLogs.push({ label: "install requirements", result: installResult });
    if (installResult.code !== 0) {
      throw new Error(`Could not install requirements.\n${installResult.stderr || installResult.stdout}`);
    }
    fs.writeFileSync(markerPath, requirements, "utf8");
  }

  async runScript(script, parameterValues) {
    const variables = this.buildVariables(parameterValues, script);
    this.addVenvVariables(script, variables);

    const cwd = stripWrappingQuotes(this.renderTemplate(script.cwd || "{{vault}}", variables).trim());
    const env = {
      ...process.env,
      ...parseEnvironment(script.env, (value) => this.renderTemplate(value, variables)),
    };
    const setupLogs = [];

    try {
      await this.ensureVenv(script, variables, cwd || undefined, env, setupLogs);
    } catch (error) {
      new Notice(`Script setup failed: ${script.name}`, 10000);
      new ScriptOutputModal(this.app, {
        script,
        command: "setup",
        args: [],
        cwd,
        startedAt: new Date(),
        finishedAt: new Date(),
        code: null,
        signal: null,
        stdout: "",
        stderr: error.stack || error.message,
        setupLogs,
      }).open();
      return;
    }

    const command = stripWrappingQuotes(this.renderTemplate(script.command, variables).trim());
    const args = parseArgumentLines(script.arguments).map((arg) => this.renderTemplate(arg, variables));
    if (!command) {
      new Notice("Vault Script Runner: command is empty.");
      return;
    }

    new Notice(`Running script: ${script.name}`);
    const result = await runProcess(command, args, {
      cwd: cwd || undefined,
      env,
      shell: Boolean(script.runInShell),
    });

    result.script = script;
    result.command = command;
    result.args = args;
    result.cwd = cwd;
    result.setupLogs = setupLogs;

    if (result.code === 0) {
      new Notice(`Script finished: ${script.name}`);
    } else {
      new Notice(`Script failed (${result.code ?? result.signal ?? "unknown"}): ${script.name}`, 10000);
    }

    if (script.openOutput !== false || result.code !== 0 || setupLogs.length > 0) {
      new ScriptOutputModal(this.app, result).open();
    }
  }
};

class ScriptPickerModal extends Modal {
  constructor(app, plugin, scripts) {
    super(app);
    this.plugin = plugin;
    this.scripts = scripts;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: "Run script" });
    const list = contentEl.createDiv({ cls: "vault-script-runner-picker" });
    for (const script of this.scripts) {
      const button = list.createEl("button", { text: script.name });
      button.addEventListener("click", () => {
        this.close();
        this.plugin.openRunModal(script);
      });
    }
  }

  onClose() {
    this.contentEl.empty();
  }
}

class ScriptRunModal extends Modal {
  constructor(app, plugin, script) {
    super(app);
    this.plugin = plugin;
    this.script = script;
    this.inputs = new Map();
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: this.script.name });
    const parameters = normalizeParameters(this.script.parameters);
    const defaults = this.plugin.buildVariables({}, this.script);

    if (parameters.length === 0) {
      contentEl.createEl("p", { text: "This script has no parameters.", cls: "vault-script-runner-help" });
    }

    for (const parameter of parameters) {
      const field = contentEl.createDiv({ cls: "vault-script-runner-field" });
      field.createEl("label", { text: parameter.label || parameter.name });
      const input = field.createEl("input", {
        type: parameter.secret ? "password" : "text",
        placeholder: parameter.placeholder || "",
        value: this.plugin.renderTemplate(parameter.defaultValue || "", defaults),
      });
      this.inputs.set(parameter.name, input);
    }

    const actions = contentEl.createDiv({ cls: "vault-script-runner-actions" });
    actions.createEl("button", { text: "Cancel" }).addEventListener("click", () => this.close());
    const run = actions.createEl("button", { text: "Run" });
    run.addClass("mod-cta");
    run.addEventListener("click", () => this.submit());
    const firstInput = this.inputs.values().next().value;
    if (firstInput) firstInput.focus();
    else run.focus();
  }

  submit() {
    const values = {};
    const parameters = normalizeParameters(this.script.parameters);
    const defaults = this.plugin.buildVariables({}, this.script);
    for (const parameter of parameters) {
      const input = this.inputs.get(parameter.name);
      const rawValue = input ? input.value.trim() : "";
      const fallback = this.plugin.renderTemplate(parameter.defaultValue || "", defaults).trim();
      values[parameter.name] = stripWrappingQuotes(rawValue || fallback);
    }
    this.close();
    this.plugin.runScript(this.script, values);
  }

  onClose() {
    this.contentEl.empty();
  }
}

class ScriptOutputModal extends Modal {
  constructor(app, result) {
    super(app);
    this.result = result;
  }

  onOpen() {
    const { contentEl } = this;
    const result = this.result;
    contentEl.empty();
    contentEl.createEl("h2", { text: result.code === 0 ? "Script finished" : "Script output" });
    const durationMs = result.finishedAt.getTime() - result.startedAt.getTime();
    contentEl.createEl("div", {
      cls: "vault-script-runner-output-meta",
      text: [
        `Script: ${result.script.name}`,
        `Exit: ${result.code === null ? result.signal || "unknown" : result.code}`,
        `Duration: ${(durationMs / 1000).toFixed(1)}s`,
        `Working directory: ${result.cwd || "(default)"}`,
        `Command: ${formatCommandLine(result.command, result.args)}`,
      ].join("\n"),
    });

    if (Array.isArray(result.setupLogs) && result.setupLogs.length > 0) {
      contentEl.createEl("h3", { text: "setup" });
      for (const entry of result.setupLogs) {
        contentEl.createEl("pre", { cls: "vault-script-runner-output", text: formatSetupLog(entry) });
      }
    }

    contentEl.createEl("h3", { text: "stdout" });
    contentEl.createEl("pre", { cls: "vault-script-runner-output", text: result.stdout || "(empty)" });
    contentEl.createEl("h3", { text: "stderr" });
    contentEl.createEl("pre", { cls: "vault-script-runner-output", text: result.stderr || "(empty)" });
  }

  onClose() {
    this.contentEl.empty();
  }
}

class VaultScriptRunnerSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();

    new Setting(containerEl)
      .setName("Python executable")
      .setDesc("Used to create shared virtual environments.")
      .addText((text) => {
        text.setPlaceholder("python").setValue(this.plugin.settings.pythonExecutable || "").onChange(async (value) => {
          this.plugin.settings.pythonExecutable = value;
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("Default virtual environment path")
      .setDesc("Relative paths resolve from the vault. Templates are supported.")
      .addText((text) => {
        text.setPlaceholder("{{pluginDir}}/.venv").setValue(this.plugin.settings.defaultVenvPath || "").onChange(async (value) => {
          this.plugin.settings.defaultVenvPath = value;
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("Downloads folder")
      .setDesc("Used by {{downloads}} and {{latestDownload}}. Leave empty to auto-detect (honors XDG user-dirs on Linux). Supports ~ and templates.")
      .addText((text) => {
        text.setPlaceholder(resolveDownloadsDir()).setValue(this.plugin.settings.downloadsDir || "").onChange(async (value) => {
          this.plugin.settings.downloadsDir = value;
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("Script catalog URL")
      .setDesc("Catalog JSON. Supports HTTPS, file://, absolute local paths, and templates.")
      .addText((text) => {
        text.setPlaceholder("https://raw.githubusercontent.com/user/repo/main/catalog/catalog.json")
          .setValue(this.plugin.settings.scriptCatalogUrl || "")
          .onChange(async (value) => {
            this.plugin.settings.scriptCatalogUrl = value;
            this.plugin.scriptCatalog = null;
            this.plugin.scriptCatalogError = "";
            await this.plugin.saveSettings();
          });
      })
      .addButton((button) => {
        button.setButtonText("Refresh").onClick(async () => {
          try {
            await this.plugin.fetchScriptCatalog();
            new Notice("Script catalog refreshed.");
          } catch (error) {
            this.plugin.scriptCatalogError = error.message;
            new Notice(`Could not refresh catalog: ${error.message}`, 10000);
          }
          this.display();
        });
      });

    this.renderCatalog(containerEl);

    new Setting(containerEl)
      .setName("Add script")
      .setDesc("Create a blank script preset manually.")
      .addButton((button) => {
        button.setButtonText("Add").onClick(async () => {
          this.plugin.settings.scripts.push(createBlankScript());
          await this.plugin.saveSettings();
          this.display();
        });
      });

    new Setting(containerEl)
      .setName("Add Python script")
      .setDesc("Create a Python preset that uses the shared virtual environment.")
      .addButton((button) => {
        button.setButtonText("Add").onClick(async () => {
          this.plugin.settings.scripts.push(createPythonScript());
          await this.plugin.saveSettings();
          this.display();
        });
      });

    this.plugin.settings.scripts.forEach((script, index) => this.renderScript(containerEl, script, index));
  }

  renderCatalog(containerEl) {
    const wrapper = containerEl.createDiv({ cls: "vault-script-runner-script" });
    wrapper.createEl("h3", { text: "Script catalog" });

    if (this.plugin.scriptCatalogError) {
      wrapper.createEl("p", { cls: "vault-script-runner-help", text: `Last refresh failed: ${this.plugin.scriptCatalogError}` });
    }
    if (!this.plugin.scriptCatalog && !this.plugin.scriptCatalogError) {
      wrapper.createEl("p", { cls: "vault-script-runner-help", text: "Loading script catalog..." });
      this.loadCatalogForSettings();
      return;
    }

    if (!this.plugin.scriptCatalog) {
      wrapper.createEl("p", { cls: "vault-script-runner-help", text: "Refresh the catalog to list downloadable scripts." });
      return;
    }

    const entries = this.plugin.scriptCatalog.scripts || [];
    const downloads = entries.filter((entry) => this.plugin.getCatalogInstallState(entry).status === "download");
    const updates = entries.filter((entry) => this.plugin.getCatalogInstallState(entry).status === "update");
    const current = entries.filter((entry) => this.plugin.getCatalogInstallState(entry).status === "installed");

    this.renderCatalogGroup(wrapper, "Available downloads", downloads, "Download");
    this.renderCatalogGroup(wrapper, "Updates", updates, "Update");
    if (current.length > 0) {
      wrapper.createEl("p", {
        cls: "vault-script-runner-help",
        text: `Installed and current: ${current.map((entry) => `${entry.name} ${entry.version}`).join(", ")}`,
      });
    }
    if (downloads.length === 0 && updates.length === 0 && current.length === 0) {
      wrapper.createEl("p", { cls: "vault-script-runner-help", text: "The catalog contains no scripts." });
    }
  }

  renderCatalogGroup(wrapper, title, entries, buttonText) {
    if (entries.length === 0) return;
    wrapper.createEl("h4", { text: title });
    for (const entry of entries) {
      const state = this.plugin.getCatalogInstallState(entry);
      new Setting(wrapper)
        .setName(`${entry.name} ${entry.version || ""}`.trim())
        .setDesc(entry.description || `Target: ${state.scriptPath}`)
        .addButton((button) => {
          button.setButtonText(buttonText).onClick(async () => {
            try {
              await this.plugin.installCatalogScript(entry);
              await this.plugin.fetchScriptCatalog();
              new Notice(`${buttonText} complete: ${entry.name}`);
            } catch (error) {
              new Notice(`Could not ${buttonText.toLowerCase()} ${entry.name}: ${error.message}`, 10000);
            }
            this.display();
          });
        });
    }
  }

  loadCatalogForSettings() {
    if (this.catalogLoadPromise) return;
    this.catalogLoadPromise = this.plugin.fetchScriptCatalog()
      .catch((error) => {
        this.plugin.scriptCatalogError = error.message;
      })
      .finally(() => {
        this.catalogLoadPromise = null;
        this.display();
      });
  }

  renderScript(containerEl, script, index) {
    const wrapper = containerEl.createEl("details", { cls: "vault-script-runner-script" });
    const summary = wrapper.createEl("summary", { cls: "vault-script-runner-script-summary" });
    summary.createEl("span", { cls: "vault-script-runner-script-title", text: script.name || `Script ${index + 1}` });

    if (script.catalogScriptId) {
      wrapper.createEl("p", { cls: "vault-script-runner-help", text: `Catalog script: ${script.catalogScriptId}` });
    }

    new Setting(wrapper).setName("Name").addText((text) => {
      text.setValue(script.name || "").onChange(async (value) => {
        script.name = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Command").addText((text) => {
      text.setPlaceholder("{{venvPython}}").setValue(script.command || "").onChange(async (value) => {
        script.command = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Working directory").addText((text) => {
      text.setPlaceholder("{{vault}}").setValue(script.cwd || "").onChange(async (value) => {
        script.cwd = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper)
      .setName("Arguments")
      .setDesc("One argument per line. Blank lines and # comments are ignored.")
      .addTextArea((text) => {
        text.inputEl.rows = 10;
        text.inputEl.cols = 60;
        text.setValue(script.arguments || "").onChange(async (value) => {
          script.arguments = value;
          await this.plugin.saveSettings();
        });
      });

    new Setting(wrapper)
      .setName("Parameters")
      .setDesc("Comma-separated prompt names.")
      .addText((text) => {
        text.setValue(normalizeParameters(script.parameters).map((parameter) => parameter.name).join(", ")).onChange(async (value) => {
          script.parameters = parseParameterNames(value).map((name) => {
            const existing = normalizeParameters(script.parameters).find((parameter) => parameter.name === name);
            return existing || { name, label: humanize(name), placeholder: "", defaultValue: "" };
          });
          await this.plugin.saveSettings();
        });
      });

    new Setting(wrapper).setName("Use virtual environment").addToggle((toggle) => {
      toggle.setValue(Boolean(script.useVenv)).onChange(async (value) => {
        script.useVenv = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Requirements").addTextArea((text) => {
      text.inputEl.rows = 5;
      text.inputEl.cols = 60;
      text.setValue(script.requirements || "").onChange(async (value) => {
        script.requirements = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Environment").addTextArea((text) => {
      text.inputEl.rows = 4;
      text.inputEl.cols = 60;
      text.setValue(script.env || "").onChange(async (value) => {
        script.env = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Run in shell").addToggle((toggle) => {
      toggle.setValue(Boolean(script.runInShell)).onChange(async (value) => {
        script.runInShell = value;
        await this.plugin.saveSettings();
      });
    });

    new Setting(wrapper).setName("Open output").addToggle((toggle) => {
      toggle.setValue(script.openOutput !== false).onChange(async (value) => {
        script.openOutput = value;
        await this.plugin.saveSettings();
      });
    });

    const removeDesc = script.catalogScriptId
      ? "Removes the preset and uninstalls the downloaded script file, so it can be downloaded again from the catalog."
      : "Removes this preset.";
    new Setting(wrapper)
      .setName("Remove preset")
      .setDesc(removeDesc)
      .addButton((button) => {
        button.setWarning().setButtonText("Remove").onClick(async () => {
          const [removed] = this.plugin.settings.scripts.splice(index, 1);
          const catalogId = removed?.catalogScriptId;
          if (catalogId && this.plugin.settings.installedScripts?.[catalogId]) {
            const installed = this.plugin.settings.installedScripts[catalogId];
            const scriptPath = path.join(this.plugin.getScriptsDir(), installed.fileName);
            try {
              if (fs.existsSync(scriptPath)) {
                fs.unlinkSync(scriptPath);
              }
            } catch (error) {
              new Notice(`Removed preset, but could not delete ${installed.fileName}: ${error.message}`, 8000);
            }
            delete this.plugin.settings.installedScripts[catalogId];
          }
          await this.plugin.saveSettings();
          this.display();
        });
      });
  }
}

function normalizeCatalogEntry(entry) {
  if (!entry || !entry.id || !entry.name || !(entry.url || entry.path || entry.fileName)) {
    return null;
  }
  return {
    id: String(entry.id),
    name: String(entry.name),
    version: String(entry.version || "0.0.0"),
    description: String(entry.description || ""),
    fileName: safeScriptFileName(entry.fileName || path.basename(entry.path || entry.url || entry.id)),
    path: entry.path || "",
    url: entry.url || "",
    sha256: entry.sha256 || "",
    preset: entry.preset || null,
  };
}

function normalizeScript(script) {
  return {
    id: script.id || slugify(script.name || `script-${Date.now()}`),
    name: script.name || "Script",
    command: script.command || "",
    arguments: script.arguments || "",
    cwd: script.cwd || "{{vault}}",
    parameters: normalizeParameters(script.parameters),
    env: script.env || "",
    useVenv: Boolean(script.useVenv),
    venvPath: script.venvPath || "",
    pythonExecutable: script.pythonExecutable || "",
    requirements: script.requirements || "",
    runInShell: Boolean(script.runInShell),
    openOutput: script.openOutput !== false,
    catalogScriptId: script.catalogScriptId || "",
  };
}

function createBlankScript() {
  return normalizeScript({ id: `script-${Date.now()}`, name: "New script", cwd: "{{vault}}", openOutput: true });
}

function createPythonScript() {
  return normalizeScript({
    id: `python-script-${Date.now()}`,
    name: "New Python script",
    command: "{{venvPython}}",
    cwd: "{{vault}}",
    useVenv: true,
    openOutput: true,
  });
}

function upsertScriptPreset(scripts, preset) {
  const index = scripts.findIndex((script) => script.id === preset.id);
  if (index >= 0) scripts[index] = preset;
  else scripts.push(preset);
}

function normalizeParameters(parameters) {
  if (!Array.isArray(parameters)) return [];
  return parameters
    .map((parameter) => {
      if (typeof parameter === "string") {
        return { name: parameter, label: humanize(parameter), placeholder: "", defaultValue: "" };
      }
      return parameter;
    })
    .filter((parameter) => parameter && parameter.name);
}

function parseParameterNames(value) {
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean);
}

function parseArgumentLines(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
}

function parseEnvironment(value, renderTemplate) {
  const env = {};
  for (const line of String(value || "").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const index = trimmed.indexOf("=");
    if (index < 1) continue;
    env[trimmed.slice(0, index).trim()] = renderTemplate(trimmed.slice(index + 1));
  }
  return env;
}

function normalizeRequirementText(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"))
    .join("\n");
}

async function readTextLocation(location, baseDir) {
  if (/^https?:\/\//i.test(location)) {
    const response = await requestUrl({ url: location, method: "GET" });
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`HTTP ${response.status} for ${location}`);
    }
    return response.text;
  }

  let filePath = location;
  if (/^file:\/\//i.test(location)) {
    filePath = fileURLToPath(location);
  } else if (!path.isAbsolute(filePath)) {
    filePath = path.resolve(baseDir, filePath);
  }
  return fs.readFileSync(filePath, "utf8");
}

function resolveLocation(location, baseLocation) {
  if (!location) return "";
  if (/^https?:\/\//i.test(location) || /^file:\/\//i.test(location) || path.isAbsolute(location)) {
    return location;
  }
  if (/^https?:\/\//i.test(baseLocation)) {
    return new URL(location, baseLocation).toString();
  }
  const basePath = /^file:\/\//i.test(baseLocation) ? fileURLToPath(baseLocation) : baseLocation;
  return path.resolve(path.dirname(basePath), location);
}

function compareVersions(left, right) {
  const a = String(left).split(/[^\d]+/).filter(Boolean).map(Number);
  const b = String(right).split(/[^\d]+/).filter(Boolean).map(Number);
  const length = Math.max(a.length, b.length);
  for (let i = 0; i < length; i += 1) {
    const diff = (a[i] || 0) - (b[i] || 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

function runProcess(command, args, options) {
  return new Promise((resolve) => {
    const startedAt = new Date();
    let stdout = "";
    let stderr = "";
    const outputLimit = 300000;
    let finished = false;
    const finish = (result) => {
      if (finished) return;
      finished = true;
      resolve({
        command,
        args,
        cwd: options.cwd || "",
        startedAt,
        finishedAt: new Date(),
        code: result.code,
        signal: result.signal || null,
        stdout,
        stderr,
      });
    };

    let child;
    try {
      child = spawn(command, args, {
        cwd: options.cwd || undefined,
        env: options.env || process.env,
        shell: Boolean(options.shell),
        windowsHide: true,
      });
    } catch (error) {
      stderr = appendLimited(stderr, `${error.stack || error.message}\n`, outputLimit);
      finish({ code: null, signal: null });
      return;
    }

    child.stdout.on("data", (chunk) => {
      stdout = appendLimited(stdout, chunk.toString(), outputLimit);
    });
    child.stderr.on("data", (chunk) => {
      stderr = appendLimited(stderr, chunk.toString(), outputLimit);
    });
    child.on("error", (error) => {
      stderr = appendLimited(stderr, `${error.stack || error.message}\n`, outputLimit);
      finish({ code: null, signal: null });
    });
    child.on("close", (code, signal) => finish({ code, signal }));
  });
}

function addPathVariables(variables, prefix, rawValue) {
  const value = String(rawValue || "");
  if (!value) return;
  variables[`${prefix}.basename`] = path.basename(value);
  variables[`${prefix}.stem`] = path.basename(value, path.extname(value));
  variables[`${prefix}.dirname`] = path.dirname(value);
  variables[`${prefix}.ext`] = path.extname(value);
}

function resolveDownloadsDir() {
  const home = os.homedir();
  // On Linux the Downloads folder can be relocated via XDG user-dirs; honor it.
  if (process.platform === "linux") {
    const candidate = process.env.XDG_DOWNLOAD_DIR || readXdgDownloadDir(home);
    if (candidate) {
      const resolved = candidate.replace(/\$HOME/g, home).replace(/^~(?=[\\/]|$)/, home);
      if (resolved) return resolved;
    }
  }
  return path.join(home, "Downloads");
}

function readXdgDownloadDir(home) {
  try {
    const configHome = process.env.XDG_CONFIG_HOME || path.join(home, ".config");
    const text = fs.readFileSync(path.join(configHome, "user-dirs.dirs"), "utf8");
    const match = text.match(/^\s*XDG_DOWNLOAD_DIR\s*=\s*"([^"]*)"/m);
    return match ? match[1] : "";
  } catch (_error) {
    return "";
  }
}

function findLatestFile(directory, extension) {
  try {
    const normalizedExtension = extension ? extension.toLowerCase() : "";
    let latestPath = "";
    let latestTime = -1;
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (!entry.isFile()) continue;
      const filePath = path.join(directory, entry.name);
      if (normalizedExtension && path.extname(filePath).toLowerCase() !== normalizedExtension) continue;
      const stat = fs.statSync(filePath);
      if (stat.mtimeMs > latestTime) {
        latestTime = stat.mtimeMs;
        latestPath = filePath;
      }
    }
    return latestPath;
  } catch (_error) {
    return "";
  }
}

function getVenvPythonPath(venvPath) {
  return process.platform === "win32" ? path.join(venvPath, "Scripts", "python.exe") : path.join(venvPath, "bin", "python");
}

function appendLimited(existing, addition, limit) {
  const combined = existing + addition;
  return combined.length <= limit ? combined : combined.slice(combined.length - limit);
}

function stripWrappingQuotes(value) {
  const text = String(value || "");
  if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
    return text.slice(1, -1);
  }
  return text;
}

function readTextIfExists(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch (_error) {
    return null;
  }
}

function safeScriptFileName(value) {
  const name = path.basename(String(value || "script.py"));
  return name.replace(/[<>:"/\\|?*\x00-\x1F]/g, "-") || "script.py";
}

function uniqueCommandId(value, usedIds) {
  const base = slugify(value || "run-script");
  let candidate = base;
  let suffix = 2;
  while (usedIds.has(candidate)) {
    candidate = `${base}-${suffix}`;
    suffix += 1;
  }
  return candidate;
}

function sha256(value) {
  return crypto.createHash("sha256").update(value, "utf8").digest("hex");
}

function formatSetupLog(entry) {
  const result = entry.result;
  return [
    `$ ${formatCommandLine(result.command, result.args)}`,
    `exit: ${result.code === null ? result.signal || "unknown" : result.code}`,
    "",
    "stdout:",
    result.stdout || "(empty)",
    "",
    "stderr:",
    result.stderr || "(empty)",
  ].join("\n");
}

function formatCommandLine(command, args) {
  return [command, ...(args || [])].map(quoteForDisplay).join(" ");
}

function quoteForDisplay(value) {
  const text = String(value || "");
  return !text || /[\s"]/u.test(text) ? `"${text.replace(/"/g, '\\"')}"` : text;
}

function normalizeObsidianFolder(value) {
  const normalized = String(value || "").replace(/\\/g, "/").replace(/^\/+|\/+$/g, "");
  return normalized === "." || normalized === "/" ? "" : normalized;
}

function formatDate(date) {
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, "0"), String(date.getDate()).padStart(2, "0")].join("-");
}

function formatTime(date) {
  return [String(date.getHours()).padStart(2, "0"), String(date.getMinutes()).padStart(2, "0"), String(date.getSeconds()).padStart(2, "0")].join("-");
}

function slugify(value) {
  return String(value || "script").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "script";
}

function humanize(value) {
  return String(value || "").replace(/[_-]+/g, " ").replace(/([a-z])([A-Z])/g, "$1 $2").replace(/^./, (char) => char.toUpperCase());
}

/* nosourcemap */