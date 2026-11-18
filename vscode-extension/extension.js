"use strict";

// The grammars are generated; this module only chooses one. On open and when
// line 1 changes it reads the same header rule as the interpreter, and the
// command lets the reader override the choice for the current file.

const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

// Keep in sync with HEADER_RE in kerincilang.py.
const HEADER_RE = /^\s*#\s*dialek\s*:\s*([a-z0-9-]+)\s*$/;
const CONFIG = "kerincilang.autoDetectDialect";
const COMMAND = "kerincilang.pilihDialek";
const AUTO = "kerincilang.auto";

// uri -> language id chosen by hand; cleared when the document closes.
const overrides = new Map();

function loadCatalogue(extensionPath) {
  const file = path.join(extensionPath, "dialects.json");
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function isKerinciLang(document) {
  return document.languageId === "kerincilang" ||
    document.languageId.indexOf("kerincilang-") === 0;
}

function headerCode(document) {
  if (document.lineCount === 0) return null;
  const match = HEADER_RE.exec(document.lineAt(0).text);
  return match ? match[1] : null;
}

function detectedLanguage(document, catalogue) {
  const code = headerCode(document);
  if (!code) return catalogue.union.language;
  const found = catalogue.dialects.find((item) => item.code === code);
  return found ? found.language : catalogue.union.language;
}

function autoDetect() {
  return vscode.workspace.getConfiguration().get(CONFIG, true);
}

async function setLanguage(document, language) {
  if (!language || language === document.languageId) return;
  try {
    await vscode.languages.setTextDocumentLanguage(document, language);
  } catch (error) {
    console.error("KerinciLang: cannot switch to " + language, error);
  }
}

function apply(document, catalogue) {
  if (!isKerinciLang(document)) return;
  const key = document.uri.toString();
  const chosen = overrides.has(key)
    ? overrides.get(key)
    : (autoDetect() ? detectedLanguage(document, catalogue) : null);
  setLanguage(document, chosen);
}

async function pick(document, catalogue) {
  if (!document || !isKerinciLang(document)) {
    vscode.window.showInformationMessage("Buka berkas .krc dulu.");
    return;
  }
  const key = document.uri.toString();
  const items = [
    {
      label: "Otomatis (ikuti baris 1)",
      description: "auto",
      language: AUTO
    },
    {
      label: "Union (semua dialek)",
      description: catalogue.union.language,
      language: catalogue.union.language
    }
  ];
  for (const item of catalogue.dialects) {
    items.push({
      label: item.name,
      description: item.code + " - " + item.status,
      language: item.language
    });
  }
  const chosen = await vscode.window.showQuickPick(items, {
    placeHolder: "Pilih dialek untuk penyorotan berkas ini"
  });
  if (!chosen) return;
  if (chosen.language === AUTO) {
    overrides.delete(key);
    apply(document, catalogue);
    return;
  }
  overrides.set(key, chosen.language);
  await setLanguage(document, chosen.language);
}

function activate(context) {
  const catalogue = loadCatalogue(context.extensionPath);

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument((document) => {
      apply(document, catalogue);
    }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      const document = event.document;
      if (!isKerinciLang(document)) return;
      const touchesHeader = event.contentChanges.some(
        (change) => change.range.start.line === 0);
      if (touchesHeader) apply(document, catalogue);
    }),
    vscode.workspace.onDidCloseTextDocument((document) => {
      overrides.delete(document.uri.toString());
    }),
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (!event.affectsConfiguration(CONFIG)) return;
      overrides.clear();
      for (const document of vscode.workspace.textDocuments) {
        apply(document, catalogue);
      }
    }),
    vscode.commands.registerCommand(COMMAND, () => {
      const editor = vscode.window.activeTextEditor;
      pick(editor ? editor.document : null, catalogue);
    })
  );

  for (const document of vscode.workspace.textDocuments) {
    apply(document, catalogue);
  }
}

function deactivate() {
  overrides.clear();
}

module.exports = { activate, deactivate };
