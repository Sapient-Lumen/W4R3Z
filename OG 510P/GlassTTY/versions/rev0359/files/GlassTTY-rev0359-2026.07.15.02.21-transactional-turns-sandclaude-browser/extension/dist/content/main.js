"use strict";
(() => {
  // src/content/generic.ts
  function safeTrim(value) {
    if (typeof value !== "string") return null;
    const compact = value.replace(/\s+/g, " ").trim();
    return compact || null;
  }
  function isVisible(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none";
  }
  function textFrom(el) {
    if (!el) return null;
    if (el instanceof HTMLTextAreaElement) return safeTrim(el.value);
    if (el instanceof HTMLInputElement) return safeTrim(el.value);
    return safeTrim(el.textContent);
  }
  function selectorIdentity(node) {
    const id = safeTrim(node.getAttribute("id"));
    if (id) return `#${id}`;
    const name = safeTrim(node.getAttribute("name"));
    if (name) return `[name=${JSON.stringify(name)}]`;
    return null;
  }
  function selectorHint(node, fallback) {
    const parts = [node.tagName.toLowerCase()];
    const identity = selectorIdentity(node);
    const role = safeTrim(node.getAttribute("role"));
    const placeholder = safeTrim(node.getAttribute("placeholder"));
    const dataPlaceholder = safeTrim(node.getAttribute("data-placeholder"));
    const aria = safeTrim(node.getAttribute("aria-label"));
    if (identity) parts.push(identity);
    if (role) parts.push(`[role=${JSON.stringify(role)}]`);
    if (placeholder) parts.push(`[placeholder*=${JSON.stringify(placeholder.slice(0, 24))}]`);
    if (dataPlaceholder) parts.push(`[data-placeholder*=${JSON.stringify(dataPlaceholder.slice(0, 24))}]`);
    if (aria) parts.push(`[aria-label*=${JSON.stringify(aria.slice(0, 24))}]`);
    return parts.join(" ") || fallback;
  }
  function uniqueStrings(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      const trimmed = safeTrim(value);
      if (!trimmed || seen.has(trimmed)) continue;
      seen.add(trimmed);
      out.push(trimmed);
    }
    return out;
  }
  function labelTexts(node) {
    if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLOutputElement || node instanceof HTMLProgressElement || node instanceof HTMLMeterElement) {
      return uniqueStrings(Array.from(node.labels || []).map((label) => label.textContent));
    }
    const labelledBy = safeTrim(node.getAttribute("aria-labelledby"));
    if (!labelledBy) return [];
    return uniqueStrings(labelledBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
  }
  function descriptionTexts(node) {
    const describedBy = safeTrim(node.getAttribute("aria-describedby"));
    if (!describedBy) return [];
    return uniqueStrings(describedBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
  }
  function nearestLegend(node) {
    const fieldset = node.closest("fieldset");
    return safeTrim(fieldset?.querySelector("legend")?.textContent ?? null);
  }
  function nearestDialog(node) {
    const dialog = node.closest('dialog, [role="dialog"], [role="alertdialog"]');
    if (!(dialog instanceof Element)) return {};
    const role = safeTrim(dialog.getAttribute("role")) || (dialog.tagName === "DIALOG" ? "dialog" : null) || void 0;
    const labelledBy = safeTrim(dialog.getAttribute("aria-labelledby"));
    const labelFromRef = labelledBy ? uniqueStrings(labelledBy.split(/\s+/).map((id) => dialog.ownerDocument.getElementById(id)?.textContent ?? null))[0] : null;
    const name = labelFromRef || safeTrim(dialog.getAttribute("aria-label")) || safeTrim(dialog.querySelector("h1, h2, h3, [data-dialog-title], legend")?.textContent ?? null) || void 0;
    let modal;
    if (dialog instanceof HTMLDialogElement) {
      try {
        modal = dialog.matches(":modal");
      } catch {
        modal = dialog.hasAttribute("open");
      }
    } else {
      modal = dialog.getAttribute("aria-modal") === "true";
    }
    const open = dialog instanceof HTMLDialogElement ? dialog.open : dialog.hasAttribute("open") || dialog.getAttribute("aria-hidden") === "false";
    return { ...name ? { name } : {}, ...role ? { role } : {}, ...typeof modal === "boolean" ? { modal } : {}, open };
  }
  function formContext(node) {
    const form = node.closest("form");
    if (!(form instanceof HTMLFormElement)) return {};
    const labelledBy = safeTrim(form.getAttribute("aria-labelledby"));
    const labelFromRef = labelledBy ? uniqueStrings(labelledBy.split(/\s+/).map((id) => form.ownerDocument.getElementById(id)?.textContent ?? null))[0] : null;
    const name = labelFromRef || safeTrim(form.getAttribute("aria-label")) || safeTrim(form.querySelector("legend, h1, h2, h3, h4, h5, h6")?.textContent ?? null) || void 0;
    const action = safeTrim(form.getAttribute("action")) || safeTrim(form.action) || void 0;
    const method = safeTrim(form.getAttribute("method")) || safeTrim(form.method) || void 0;
    return { ...name ? { name } : {}, ...action ? { action } : {}, ...method ? { method } : {} };
  }
  function frameChainForWindow(win) {
    const chain = [];
    let current = win;
    while (current && current.top !== current) {
      try {
        const frame = current.frameElement;
        if (!(frame instanceof HTMLIFrameElement)) break;
        chain.unshift({
          selector: selectorHint(frame, "iframe"),
          ...safeTrim(frame.name) ? { name: safeTrim(frame.name) } : {},
          ...safeTrim(frame.title) ? { title: safeTrim(frame.title) } : {}
        });
        current = current.parent;
      } catch {
        break;
      }
    }
    return chain;
  }
  function frameContext(win) {
    const chain = frameChainForWindow(win);
    if (!chain.length) return {};
    const leaf = chain[chain.length - 1];
    const pathSelectors = chain.map((entry) => entry.selector);
    const pathNames = uniqueStrings(chain.map((entry) => entry.name ?? null));
    const pathTitles = uniqueStrings(chain.map((entry) => entry.title ?? null));
    return {
      selector: leaf.selector,
      ...leaf.name ? { name: leaf.name } : {},
      ...leaf.title ? { title: leaf.title } : {},
      ...pathSelectors.length ? { path: pathSelectors.join(" >> "), pathSelectors } : {},
      ...pathNames.length ? { pathNames } : {},
      ...pathTitles.length ? { pathTitles } : {},
      depth: chain.length
    };
  }
  function controlKind(node) {
    const role = safeTrim(node.getAttribute("role"));
    if (role) return role;
    if (node instanceof HTMLTextAreaElement) return "textarea";
    if (node instanceof HTMLSelectElement) return node.multiple ? "listbox" : "combobox";
    if (node instanceof HTMLInputElement) return `input:${(node.type || "text").toLowerCase()}`;
    if (node instanceof HTMLButtonElement) return "button";
    if (node.getAttribute("contenteditable") === "" || node.getAttribute("contenteditable") === "true") return "contenteditable";
    return node.tagName.toLowerCase();
  }
  function selectedOptions(node) {
    if (!(node instanceof HTMLSelectElement)) return [];
    return uniqueStrings(Array.from(node.selectedOptions).map((option) => option.label || option.textContent));
  }
  function optionLabels(node) {
    if (!(node instanceof HTMLSelectElement)) return [];
    return uniqueStrings(Array.from(node.options).map((option) => option.label || option.textContent));
  }
  function autocompleteValue(node) {
    if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement)) return null;
    return safeTrim(node.autocomplete || node.getAttribute("autocomplete"));
  }
  function inputModeValue(node) {
    const attr = safeTrim(node.getAttribute("inputmode"));
    if (attr) return attr;
    if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement) {
      return safeTrim(node.inputMode);
    }
    return null;
  }
  function choiceGroup(node) {
    if (node instanceof HTMLInputElement && ["checkbox", "radio"].includes((node.type || "").toLowerCase())) {
      return safeTrim(node.name) || nearestLegend(node);
    }
    return null;
  }
  function constraintHints(node) {
    const hints = [];
    if (node instanceof HTMLInputElement) {
      if (safeTrim(node.pattern)) hints.push(`pattern:${node.pattern}`);
      if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
      if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
      if (safeTrim(node.min)) hints.push(`min:${node.min}`);
      if (safeTrim(node.max)) hints.push(`max:${node.max}`);
      if (safeTrim(node.step)) hints.push(`step:${node.step}`);
    } else if (node instanceof HTMLTextAreaElement) {
      if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
      if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
    }
    return uniqueStrings(hints);
  }
  function constraintFlags(node) {
    if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement)) return [];
    const validity = node.validity;
    const flags = [];
    const known = ["badInput", "customError", "patternMismatch", "rangeOverflow", "rangeUnderflow", "stepMismatch", "tooLong", "tooShort", "typeMismatch", "valueMissing"];
    for (const key of known) {
      if (validity[key]) flags.push(key);
    }
    return flags;
  }
  function candidateInfo(node, score, fallback, win = window) {
    const labels = labelTexts(node);
    const descriptions = descriptionTexts(node);
    const fieldsetLegend = nearestLegend(node);
    const dialog = nearestDialog(node);
    const form = formContext(node);
    const frame = frameContext(win);
    const selected = selectedOptions(node);
    const options = optionLabels(node);
    const placeholder = safeTrim(node.getAttribute("placeholder")) || void 0;
    const name = safeTrim(node.getAttribute("name")) || void 0;
    const explicitRole = safeTrim(node.getAttribute("role")) || void 0;
    const accessibleNames = uniqueStrings([
      safeTrim(node.getAttribute("aria-label")),
      ...labels,
      placeholder,
      name
    ]);
    const textSample = safeTrim(node.textContent)?.slice(0, 120) || void 0;
    const control = controlKind(node) || void 0;
    const checkedState = node instanceof HTMLInputElement && ["checkbox", "radio"].includes((node.type || "").toLowerCase()) ? node.checked ? "checked" : "unchecked" : void 0;
    const readonly = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement ? node.readOnly : void 0;
    const disabled = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLButtonElement ? node.disabled : void 0;
    const multiple = node instanceof HTMLInputElement || node instanceof HTMLSelectElement ? Boolean(node.multiple) : void 0;
    const required = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.required : void 0;
    const invalid = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.matches(":invalid") : void 0;
    const autoComplete = autocompleteValue(node) || void 0;
    const inputMode = inputModeValue(node) || void 0;
    const hintList = constraintHints(node);
    const flagList = constraintFlags(node);
    const choice = choiceGroup(node) || void 0;
    const submitAction = node instanceof HTMLButtonElement || node instanceof HTMLInputElement && ["submit", "button"].includes((node.type || "").toLowerCase()) ? form.action || void 0 : void 0;
    const submitMethod = node instanceof HTMLButtonElement || node instanceof HTMLInputElement && ["submit", "button"].includes((node.type || "").toLowerCase()) ? form.method || void 0 : void 0;
    const submitTarget = node instanceof HTMLButtonElement || node instanceof HTMLInputElement ? safeTrim(node.getAttribute("formtarget")) || void 0 : void 0;
    return {
      selector_hint: selectorHint(node, fallback),
      score: Number(score.toFixed(3)),
      text_length: (textFrom(node) || "").length,
      visible: isVisible(node),
      ...labels[0] ? { label_text: labels[0] } : {},
      ...labels.length ? { labels } : {},
      ...accessibleNames[0] ? { accessible_name: accessibleNames[0] } : {},
      ...accessibleNames.length ? { accessible_names: accessibleNames } : {},
      ...descriptions[0] ? { description_text: descriptions[0] } : {},
      ...descriptions.length ? { descriptions } : {},
      ...fieldsetLegend ? { fieldset_legend: fieldsetLegend, fieldset_legends: [fieldsetLegend] } : {},
      ...dialog.name ? { dialog_name: dialog.name } : {},
      ...dialog.role ? { dialog_role: dialog.role } : {},
      ...typeof dialog.modal === "boolean" ? { dialog_modal: dialog.modal } : {},
      ...typeof dialog.open === "boolean" ? { dialog_open: dialog.open } : {},
      ...control ? { control_kind: control } : {},
      ...form.name ? { form_name: form.name } : {},
      ...form.action ? { form_action: form.action } : {},
      ...form.method ? { form_method: form.method } : {},
      ...frame.selector ? { frame_selector: frame.selector } : {},
      ...frame.name ? { frame_name: frame.name } : {},
      ...frame.title ? { frame_title: frame.title } : {},
      ...frame.path ? { frame_path: frame.path } : {},
      ...typeof frame.depth === "number" ? { frame_depth: frame.depth } : {},
      ...frame.pathSelectors?.length ? { frame_path_selectors: frame.pathSelectors } : {},
      ...frame.pathNames?.length ? { frame_path_names: frame.pathNames } : {},
      ...frame.pathTitles?.length ? { frame_path_titles: frame.pathTitles } : {},
      ...options.length ? { option_count: options.length, option_labels: options } : {},
      ...selected.length ? { selected_options: selected, selected_count: selected.length } : {},
      ...typeof required === "boolean" ? { required } : {},
      ...typeof invalid === "boolean" ? { invalid } : {},
      ...checkedState ? { checked_state: checkedState } : {},
      ...typeof disabled === "boolean" ? { disabled } : {},
      ...typeof readonly === "boolean" ? { readonly } : {},
      ...typeof multiple === "boolean" ? { multiple } : {},
      ...autoComplete ? { autocomplete: autoComplete } : {},
      ...inputMode ? { input_mode: inputMode } : {},
      ...hintList.length ? { constraint_hints: hintList } : {},
      ...flagList.length ? { constraint_flags: flagList } : {},
      ...choice ? { choice_group: choice } : {},
      ...placeholder ? { placeholder } : {},
      ...name ? { name } : {},
      ...explicitRole ? { role: explicitRole } : {},
      ...textSample ? { text_sample: textSample } : {},
      ...submitAction ? { submit_action: submitAction } : {},
      ...submitMethod ? { submit_method: submitMethod } : {},
      ...submitTarget ? { submit_target: submitTarget } : {}
    };
  }
  function iframeSampleFromElement(iframe, ownerDocument, depth, extra = {}) {
    const src = safeTrim(iframe.getAttribute("src")) || void 0;
    let resolvedSrc;
    if (src) {
      try {
        resolvedSrc = new URL(src, ownerDocument.baseURI).href;
      } catch {
        resolvedSrc = void 0;
      }
    }
    const name = safeTrim(iframe.getAttribute("name")) || void 0;
    const title = safeTrim(iframe.getAttribute("title")) || void 0;
    return {
      selectorHint: selectorHint(iframe, "iframe"),
      depth,
      ...src ? { src } : {},
      ...resolvedSrc ? { resolvedSrc } : {},
      ...name ? { name } : {},
      ...title ? { title } : {},
      ...extra
    };
  }
  function accessibleFrameContext(parent, iframe) {
    try {
      const frameWindow = iframe.contentWindow;
      const frameDocument = iframe.contentDocument || frameWindow?.document || null;
      if (!frameWindow || !frameDocument || !frameDocument.documentElement) return null;
      const selector = selectorHint(iframe, "iframe");
      const name = safeTrim(iframe.getAttribute("name")) || void 0;
      const title = safeTrim(iframe.getAttribute("title")) || void 0;
      const pathSelectors = [...parent.frame_path_selectors, selector];
      const pathNames = uniqueStrings([...parent.frame_path_names, name]);
      const pathTitles = uniqueStrings([...parent.frame_path_titles, title]);
      return {
        document: frameDocument,
        window: frameWindow,
        depth: parent.depth + 1,
        frame_selector: selector,
        ...name ? { frame_name: name } : {},
        ...title ? { frame_title: title } : {},
        ...pathSelectors.length ? { frame_path: pathSelectors.join(" >> ") } : {},
        frame_path_selectors: pathSelectors,
        frame_path_names: pathNames,
        frame_path_titles: pathTitles
      };
    } catch {
      return null;
    }
  }
  function collectLiveFrameInventory(rootDocument = document, rootWindow = window, maxDepth = 4) {
    const rootContext = {
      document: rootDocument,
      window: rootWindow,
      depth: 0,
      frame_path_selectors: [],
      frame_path_names: [],
      frame_path_titles: []
    };
    const contexts = [rootContext];
    const queue = [rootContext];
    const iframeSamples = [];
    const blockedIframeSamples = [];
    const visitedDocuments = /* @__PURE__ */ new Set([rootDocument]);
    let accessibleIframeCount = 0;
    let blockedIframeCount = 0;
    let maxFrameDepth = 0;
    while (queue.length) {
      const context = queue.shift();
      maxFrameDepth = Math.max(maxFrameDepth, context.depth);
      if (context.depth >= maxDepth) continue;
      const iframes = Array.from(context.document.querySelectorAll("iframe"));
      for (const iframe of iframes) {
        if (!(iframe instanceof HTMLIFrameElement)) continue;
        const nextContext = accessibleFrameContext(context, iframe);
        const pathSelectors = [...context.frame_path_selectors, selectorHint(iframe, "iframe")];
        const path = pathSelectors.join(" >> ");
        if (nextContext && !visitedDocuments.has(nextContext.document)) {
          accessibleIframeCount += 1;
          visitedDocuments.add(nextContext.document);
          contexts.push(nextContext);
          queue.push(nextContext);
          iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
            accessible: true,
            ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
          }));
          continue;
        }
        if (nextContext) {
          iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
            accessible: true,
            ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
          }));
          continue;
        }
        blockedIframeCount += 1;
        const blocked = iframeSampleFromElement(iframe, context.document, context.depth + 1, {
          accessible: false,
          reason: "cross-origin-or-inaccessible",
          ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
        });
        iframeSamples.push(blocked);
        blockedIframeSamples.push(blocked);
      }
    }
    const totalIframeCount = iframeSamples.length;
    const frameCaptureStatus = totalIframeCount === 0 ? "no_iframes" : accessibleIframeCount === 0 && blockedIframeCount > 0 ? "blocked_only" : blockedIframeCount > 0 ? "partial" : "full";
    const frameCaptureRatio = totalIframeCount > 0 ? Number((accessibleIframeCount / totalIframeCount).toFixed(3)) : 1;
    return {
      contexts,
      iframe_samples: iframeSamples.slice(0, 16),
      accessible_iframe_count: accessibleIframeCount,
      blocked_iframe_count: blockedIframeCount,
      blocked_iframe_samples: blockedIframeSamples.slice(0, 8),
      blocked_iframe_names: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.name === "string" ? sample.name : null)),
      blocked_iframe_titles: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.title === "string" ? sample.title : null)),
      blocked_frame_paths: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.framePath === "string" ? sample.framePath : null)),
      traversed_document_count: contexts.length,
      total_iframe_count: totalIframeCount,
      frame_capture_ratio: frameCaptureRatio,
      frame_capture_status: frameCaptureStatus,
      max_frame_depth: maxFrameDepth,
      frame_paths: uniqueStrings(contexts.slice(1).map((context) => context.frame_path ?? null))
    };
  }
  function semanticOutlineFromInventory(inventory, inputs, submits = []) {
    const headings = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("h1, h2, h3, h4, h5, h6")).map((heading) => heading.textContent)));
    const forms = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("form")));
    const dialogs = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')));
    const iframes = inventory.iframe_samples;
    const allCandidates = [...inputs, ...submits];
    const stateFlags = uniqueStrings(allCandidates.flatMap((item) => {
      const flags = [];
      if (item.required) flags.push("required");
      if (item.invalid) flags.push("invalid");
      if (item.disabled) flags.push("disabled");
      if (item.readonly) flags.push("readonly");
      if (item.multiple) flags.push("multiple");
      if (item.checked_state) flags.push(`checked:${item.checked_state}`);
      return flags;
    }));
    const linkHosts = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("a[href]")).map((link) => {
      try {
        return new URL(link.href, context.document.baseURI).host;
      } catch {
        return null;
      }
    })));
    return {
      heading_outline: headings,
      prompt_labels: uniqueStrings(inputs.flatMap((item) => [item.label_text, ...item.labels || []])),
      accessible_names: uniqueStrings(inputs.flatMap((item) => [item.accessible_name, ...item.accessible_names || []])),
      prompt_descriptions: uniqueStrings(inputs.flatMap((item) => [item.description_text, ...item.descriptions || []])),
      submit_labels: uniqueStrings(submits.flatMap((item) => [item.accessible_name, item.label_text, item.text_sample])),
      form_names: uniqueStrings([
        ...inputs.map((item) => item.form_name || null),
        ...forms.map((form) => safeTrim(form.getAttribute("aria-label")) || safeTrim(form.querySelector("legend, h1, h2, h3, h4, h5, h6")?.textContent ?? null))
      ]),
      form_actions: uniqueStrings([
        ...inputs.map((item) => item.form_action || null),
        ...submits.map((item) => item.submit_action || item.form_action || null),
        ...forms.map((form) => form instanceof HTMLFormElement ? safeTrim(form.action) : null)
      ]),
      fieldset_legends: uniqueStrings(inputs.flatMap((item) => [item.fieldset_legend, ...item.fieldset_legends || []])),
      dialog_names: uniqueStrings([
        ...inputs.map((item) => item.dialog_name || null),
        ...dialogs.map((dialog) => safeTrim(dialog.getAttribute("aria-label")) || safeTrim(dialog.querySelector("h1, h2, h3, legend")?.textContent ?? null))
      ]),
      iframe_names: uniqueStrings([
        ...inputs.flatMap((item) => [item.frame_name, ...item.frame_path_names || []]),
        ...iframes.map((frame) => typeof frame.name === "string" ? frame.name : null)
      ]),
      iframe_titles: uniqueStrings([
        ...inputs.flatMap((item) => [item.frame_title, ...item.frame_path_titles || []]),
        ...iframes.map((frame) => typeof frame.title === "string" ? frame.title : null)
      ]),
      frame_paths: uniqueStrings([
        ...inputs.map((item) => item.frame_path || null),
        ...inventory.frame_paths,
        ...iframes.map((frame) => typeof frame.framePath === "string" ? frame.framePath : null)
      ]),
      control_kinds: uniqueStrings(inputs.map((item) => item.control_kind || null)),
      option_labels: uniqueStrings(inputs.flatMap((item) => item.option_labels || [])),
      choice_groups: uniqueStrings(inputs.map((item) => item.choice_group || null)),
      autocomplete_tokens: uniqueStrings(inputs.map((item) => item.autocomplete || null)),
      state_flags: stateFlags,
      constraint_hints: uniqueStrings(inputs.flatMap((item) => item.constraint_hints || [])),
      link_hosts: linkHosts
    };
  }
  function dialogSamplesFromInventory(inventory) {
    return inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')).slice(0, 8).map((dialog) => {
      const ctx = nearestDialog(dialog);
      return {
        selectorHint: selectorHint(dialog, "dialog"),
        ...ctx.name ? { name: ctx.name } : {},
        ...ctx.role ? { role: ctx.role } : {},
        ...typeof ctx.modal === "boolean" ? { modal: ctx.modal } : {},
        ...typeof ctx.open === "boolean" ? { open: ctx.open } : {},
        ...context.frame_path ? { framePath: context.frame_path, framePathSelectors: context.frame_path_selectors } : {}
      };
    })).slice(0, 16);
  }
  function iframeSamplesFromInventory(inventory) {
    return inventory.iframe_samples.slice(0, 16);
  }
  function countAcrossContexts(inventory, selector) {
    return inventory.contexts.reduce((total, context) => total + context.document.querySelectorAll(selector).length, 0);
  }
  function buildLiveFixtureMetadata(document2, inputNode, submitNode = null, inputInfo, submitInfo, options = {}) {
    const inventory = options.inventory || collectLiveFrameInventory(document2, window);
    const computedInput = inputNode ? inputInfo || candidateInfo(inputNode, 1, selectorHint(inputNode, "input")) : null;
    const computedSubmit = submitNode ? submitInfo || candidateInfo(submitNode, 1, selectorHint(submitNode, "button")) : null;
    const inputs = options.inputCandidates?.length ? options.inputCandidates : computedInput ? [computedInput] : [];
    const outputs = options.outputCandidates?.length ? options.outputCandidates : [];
    const submits = options.submitCandidates?.length ? options.submitCandidates : computedSubmit ? [computedSubmit] : [];
    const primaryInput = computedInput || inputs[0] || null;
    const primaryOutput = outputs[0] || null;
    const primarySubmit = computedSubmit || submits[0] || null;
    const outline = semanticOutlineFromInventory(inventory, inputs, submits);
    const dialogs = dialogSamplesFromInventory(inventory);
    const iframes = iframeSamplesFromInventory(inventory);
    const frameCaptureWarning = inventory.frame_capture_status === "partial" ? `frame capture is partial: ${inventory.accessible_iframe_count}/${inventory.total_iframe_count} iframes were accessible and ${inventory.blocked_iframe_count} were blocked` : inventory.frame_capture_status === "blocked_only" ? `frame capture could not descend into any iframe: ${inventory.blocked_iframe_count} blocked iframe${inventory.blocked_iframe_count === 1 ? "" : "s"} observed` : null;
    return {
      link_count: countAcrossContexts(inventory, "a[href]"),
      form_count: countAcrossContexts(inventory, "form"),
      dialog_count: countAcrossContexts(inventory, 'dialog, [role="dialog"], [role="alertdialog"]'),
      iframe_count: countAcrossContexts(inventory, "iframe"),
      heading_count: countAcrossContexts(inventory, "h1, h2, h3, h4, h5, h6"),
      accessible_iframe_count: inventory.accessible_iframe_count,
      blocked_iframe_count: inventory.blocked_iframe_count,
      blocked_iframe_names: inventory.blocked_iframe_names,
      blocked_iframe_titles: inventory.blocked_iframe_titles,
      blocked_frame_paths: inventory.blocked_frame_paths,
      traversed_document_count: inventory.traversed_document_count,
      total_iframe_count: inventory.total_iframe_count,
      frame_capture_ratio: inventory.frame_capture_ratio,
      frame_capture_status: inventory.frame_capture_status,
      ...frameCaptureWarning ? { frame_capture_warning: frameCaptureWarning } : {},
      max_frame_depth: inventory.max_frame_depth,
      frame_paths: outline.frame_paths,
      blocked_iframe_samples: inventory.blocked_iframe_samples,
      split_scope_detected: (primaryInput?.frame_path ?? null) !== (primaryOutput?.frame_path ?? null),
      top_input_label: primaryInput?.label_text ?? null,
      top_input_accessible_name: primaryInput?.accessible_name ?? primaryInput?.label_text ?? null,
      top_input_description: primaryInput?.description_text ?? null,
      top_output_label: primaryOutput?.accessible_name ?? primaryOutput?.label_text ?? primaryOutput?.text_sample ?? null,
      top_output_frame_path: primaryOutput?.frame_path ?? null,
      top_output_frame_depth: primaryOutput?.frame_depth ?? null,
      top_fieldset_legend: primaryInput?.fieldset_legend ?? null,
      top_dialog_name: primaryInput?.dialog_name ?? null,
      top_form_name: primaryInput?.form_name ?? null,
      top_input_frame_path: primaryInput?.frame_path ?? null,
      top_input_frame_depth: primaryInput?.frame_depth ?? null,
      top_option_count: primaryInput?.option_count ?? null,
      top_selected_option: primaryInput?.selected_options?.[0] ?? null,
      top_checked_state: primaryInput?.checked_state ?? null,
      top_disabled: primaryInput?.disabled ?? false,
      top_readonly: primaryInput?.readonly ?? false,
      top_multiple: primaryInput?.multiple ?? false,
      top_selected_count: primaryInput?.selected_count ?? null,
      top_autocomplete: primaryInput?.autocomplete ?? null,
      top_input_mode: primaryInput?.input_mode ?? null,
      top_choice_group: primaryInput?.choice_group ?? null,
      top_constraint_hints: primaryInput?.constraint_hints ?? [],
      top_constraint_flags: primaryInput?.constraint_flags ?? [],
      top_submit_label: primarySubmit?.accessible_name ?? primarySubmit?.label_text ?? primarySubmit?.text_sample ?? null,
      top_submit_action: primarySubmit?.submit_action ?? primarySubmit?.form_action ?? null,
      top_submit_frame_path: primarySubmit?.frame_path ?? null,
      submit_candidates: submits,
      semantic_outline: outline,
      dialog_samples: dialogs,
      iframe_samples: iframes,
      form_actions: outline.form_actions
    };
  }

  // src/adapters/surface-probe.ts
  var SURFACE_PROBE_VERSION = "rev0359";
  var VOLATILE_ID_PATTERNS = [/^radix-/i, /^:r[0-9a-z]+:$/i, /^headlessui-/i, /^mui-/i, /^react-aria-/i];
  function isVolatileId(id) {
    if (!id) return true;
    return VOLATILE_ID_PATTERNS.some((pattern) => pattern.test(id));
  }
  var ROLE_ATLAS = [
    // The prompt editor itself. It is picked up by the interactive-node sweep
    // (role=textbox), and leaving it 'unknown' would make every healthy composer
    // report an oddity — the classic detector that nobody reads.
    { role: "composer", ids: ["prompt-textarea"], testIds: ["prompt-textarea"], terms: ["chat with chatgpt", "ask chatgpt"] },
    { role: "send", ids: ["composer-submit-button"], testIds: ["send-button"], terms: ["send prompt", "send message"] },
    { role: "stop", testIds: ["stop-button"], terms: ["stop generating", "stop streaming", "stop responding", "stop response"] },
    { role: "continue", terms: ["continue generating", "continue response"] },
    {
      role: "attach",
      ids: ["composer-plus-btn", "upload-files", "upload-photos", "upload-camera"],
      testIds: ["composer-plus-btn", "upload-photos-input"],
      terms: ["add files and more", "add files", "add photos", "attach", "upload file"]
    },
    { role: "dictate", terms: ["dictate", "microphone", "voice mode", "start dictation", "start voice"] },
    { role: "model-picker", testIds: ["model-switcher-dropdown-button"], terms: ["model selector", "switch model", "choose model"] },
    // The composer pill. Live report shows it as a __composer-pill button whose
    // text is the current effort tier ("Pro"). Its id is volatile (radix-*), so it
    // is matched by class/text, never by id.
    { role: "effort-pill", classes: ["__composer-pill"], terms: ["instant", "medium", "high", "extra high", "pro"] },
    { role: "tools", terms: ["tools", "deep research", "create image", "canvas"] },
    { role: "search", terms: ["search chats", "search"] },
    { role: "copy", testIds: ["copy-turn-action-button"], terms: ["copy", "copy code", "copy response"] },
    { role: "edit", terms: ["edit message", "edit in canvas"] },
    { role: "regenerate", terms: ["regenerate", "try again", "retry"] },
    { role: "feedback", testIds: ["good-response-turn-action-button", "bad-response-turn-action-button"], terms: ["good response", "bad response", "thumbs"] },
    { role: "scroll", terms: ["scroll to bottom"] },
    { role: "new-chat", testIds: ["create-new-chat-button"], terms: ["new chat"] },
    { role: "conversation-options", testIds: ["conversation-options-button"], terms: ["conversation options", "open conversation options", "pin "] },
    { role: "citation", testIds: ["webpage-citation-pill"], terms: ["sources"] },
    { role: "sidebar", testIds: ["close-sidebar-button"], terms: ["sidebar", "open sidebar", "close sidebar"] },
    { role: "account", testIds: ["accounts-profile-button"], terms: ["account", "profile", "settings", "upgrade", "log in", "sign up", "download apps"] },
    { role: "share", terms: ["share"] },
    { role: "close", terms: ["close", "dismiss"] },
    // The signed-in root page renders these legal/help links inside the composer
    // form. Match exact link text so a future action button containing the same
    // words remains visible to the oddity hunter.
    { role: "nav", exactTexts: ["terms", "privacy policy", "learn more"] }
  ];
  function lower(value) {
    return (value || "").trim().toLowerCase();
  }
  function classify(control) {
    const id = lower(control.id);
    const testId = lower(control.test_id);
    const text = lower(control.text);
    const combined = [control.aria_label, control.title, control.text, control.test_id].map(lower).filter(Boolean).join(" | ");
    for (const matcher of ROLE_ATLAS) {
      const evidence = [];
      if (matcher.ids?.some((candidate) => candidate === id)) evidence.push(`id=${id}`);
      if (matcher.testIds?.some((candidate) => candidate === testId)) evidence.push(`data-testid=${testId}`);
      if (matcher.classes?.some((candidate) => control.class_tokens?.includes(candidate))) {
        evidence.push(`class=${matcher.classes.find((candidate) => control.class_tokens?.includes(candidate))}`);
      }
      if (matcher.terms?.some((term) => combined.includes(term))) {
        const hit = matcher.terms.find((term) => combined.includes(term));
        evidence.push(`term=${hit}`);
      }
      if (matcher.exactTexts?.some((candidate) => candidate === text)) evidence.push(`text=${text}`);
      if (evidence.length) return { role: matcher.role, evidence };
    }
    return { role: "unknown", evidence: [] };
  }
  function regionOf(node) {
    if (node.closest('[role="dialog"], dialog, [aria-modal="true"]')) return "dialog";
    if (node.closest('[role="alert"], [role="status"], [aria-live]')) return "banner";
    if (node.closest('form, #composer-background, [data-testid="composer"], [class*="composer"]')) return "composer";
    if (node.closest('nav, aside, [role="navigation"], [role="complementary"]')) return "sidebar";
    if (node.closest('header, [role="banner"]')) return "header";
    if (node.closest('main, [role="main"], article')) return "transcript";
    return "page";
  }
  function controlKey(control) {
    if (control.id && !isVolatileId(control.id)) return `id:${control.id}`;
    if (control.test_id) return `testid:${control.test_id}`;
    if (control.aria_label) return `aria:${lower(control.aria_label)}`;
    if (control.text) return `text:${lower(control.text).slice(0, 40)}`;
    return `sel:${control.selector_hint}`;
  }
  var INTERACTIVE_SELECTOR = [
    "button",
    '[role="button"]',
    '[role="menuitem"]',
    '[role="tab"]',
    '[role="switch"]',
    "a[href]",
    'input:not([type="hidden"])',
    "select",
    "textarea"
  ].join(", ");
  function probeControls(document2) {
    const controls = [];
    const seen = /* @__PURE__ */ new Set();
    for (const node of Array.from(document2.querySelectorAll(INTERACTIVE_SELECTOR))) {
      if (seen.has(node)) continue;
      seen.add(node);
      const el = node;
      const text = textFrom(node);
      const partial = {
        selector_hint: selectorHint(node, "control"),
        tag: node.tagName.toLowerCase(),
        id: node.getAttribute("id") || null,
        test_id: node.getAttribute("data-testid") || null,
        aria_label: node.getAttribute("aria-label") || null,
        title: node.getAttribute("title") || null,
        text: text ? text.slice(0, 120) : null,
        role_attr: node.getAttribute("role") || null,
        type_attr: node.getAttribute("type") || null,
        disabled: el.disabled === true || node.getAttribute("aria-disabled") === "true",
        visible: isVisible(node),
        class_tokens: Array.from(node.classList),
        region: regionOf(node)
      };
      const { role, evidence } = classify(partial);
      const withRole = { ...partial, classification: role, evidence };
      controls.push({ ...withRole, key: controlKey(withRole), id_stable: Boolean(partial.id) && !isVolatileId(partial.id) });
    }
    return controls;
  }
  function probeAnchors(document2, found, expected) {
    const anchor = (name, node, expectedSelector, detail = {}) => ({
      name,
      found: Boolean(node),
      selector_hint: node ? selectorHint(node, name) : null,
      expected_selector: expectedSelector,
      matches_expectation: Boolean(node && expectedSelector && node.matches(expectedSelector)),
      detail
    });
    return [
      anchor("composer", found.composer, expected.composer, { editable: found.composer?.isContentEditable ?? null }),
      anchor("send", found.send, expected.send, {
        test_id: found.send?.getAttribute("data-testid") ?? null,
        aria_label: found.send?.getAttribute("aria-label") ?? null,
        disabled: found.send ? found.send.disabled : null
      }),
      anchor("generation_stop", found.stop, null, {}),
      anchor("generation_continue", found.continue, null, {}),
      anchor("latest_assistant_turn", found.latestAssistant, null, {}),
      anchor("latest_user_turn", found.latestUser, null, {})
    ];
  }
  function collectOddities(controls, anchors, composer) {
    const oddities = [];
    for (const control of controls) {
      if (!control.visible) continue;
      if (control.classification === "unknown" && control.region === "composer") {
        oddities.push({
          kind: "unknown-control",
          severity: "warn",
          region: "composer",
          summary: `unclassified control in the composer: ${control.selector_hint}`,
          control
        });
      } else if (control.classification === "unknown" && control.region === "dialog") {
        oddities.push({
          kind: "dialog",
          severity: "warn",
          region: "dialog",
          summary: `unclassified control inside a modal dialog: ${control.selector_hint}`,
          control
        });
      }
    }
    const dialogControls = controls.filter((control) => control.region === "dialog" && control.visible);
    if (dialogControls.length) {
      oddities.push({
        kind: "dialog",
        severity: "warn",
        region: "dialog",
        summary: `a modal dialog is open (${dialogControls.length} control(s)); it may be intercepting clicks`
      });
    }
    const bannerControls = controls.filter((control) => control.region === "banner" && control.visible);
    if (bannerControls.length) {
      oddities.push({
        kind: "banner",
        severity: "info",
        region: "banner",
        summary: `a live/alert region is present (${bannerControls.length} control(s)); possible nag, error, or rate-limit notice`
      });
    }
    for (const item of anchors) {
      if (!item.found) {
        if (item.name === "send" && composer.present && composer.empty) {
          oddities.push({
            kind: "send-hidden-empty-composer",
            severity: "info",
            region: "composer",
            summary: "no send control, but the composer is empty \u2014 ChatGPT only renders send once you type. Probe with a draft for a definitive reading.",
            anchor: "send"
          });
          continue;
        }
        const critical = item.name === "composer" || item.name === "send";
        oddities.push({
          kind: "missing-anchor",
          severity: critical ? "critical" : "info",
          region: "page",
          summary: `anchor not found: ${item.name}`,
          anchor: item.name
        });
      } else if (item.expected_selector && !item.matches_expectation) {
        oddities.push({
          kind: "unexpected-anchor-selector",
          severity: "critical",
          region: "page",
          summary: `anchor '${item.name}' resolved to ${item.selector_hint}, which does not match the expected selector ${item.expected_selector}`,
          anchor: item.name
        });
      }
    }
    return oddities;
  }
  var FILE_INPUT_SELECTORS = [
    'form input[type="file"]',
    '[class*="composer"] input[type="file"]',
    'input[type="file"]'
  ];
  function findFileInputs(document2) {
    const inputs = [];
    const seen = /* @__PURE__ */ new Set();
    for (const selector of FILE_INPUT_SELECTORS) {
      for (const node of Array.from(document2.querySelectorAll(selector))) {
        if (node instanceof HTMLInputElement && node.type === "file" && !node.disabled && !seen.has(node)) {
          seen.add(node);
          inputs.push(node);
        }
      }
    }
    return inputs;
  }
  function findFileInput(document2) {
    return findFileInputs(document2)[0] ?? null;
  }
  function authenticationState(document2) {
    const visible = (selector) => Array.from(document2.querySelectorAll(selector)).some(isVisible);
    const loginControlPresent = visible('[data-testid="login-button"]');
    const signupControlPresent = visible('[data-testid="signup-button"]');
    const accountControlPresent = visible('[data-testid="accounts-profile-button"]');
    const anonymous = loginControlPresent || signupControlPresent;
    return {
      posture: anonymous ? "anonymous" : accountControlPresent ? "authenticated" : "unknown",
      login_control_present: loginControlPresent,
      signup_control_present: signupControlPresent,
      account_control_present: accountControlPresent
    };
  }
  function composerState(document2, composer, controls) {
    const fileInputs = findFileInputs(document2);
    const fileInput = fileInputs[0] ?? null;
    const text = composer ? (composer.textContent || "").trim() : "";
    const inputFiles = fileInputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
    const attachmentChips = controls.filter((control) => control.region === "composer" && control.visible && control.classification === "attachment-chip").length;
    return {
      present: Boolean(composer),
      empty: text.length === 0,
      text_length: text.length,
      file_input_present: Boolean(fileInput),
      file_input_selector: fileInput ? selectorHint(fileInput, "file-input") : null,
      file_input_multiple: Boolean(fileInput?.multiple),
      attachment_chip_count: attachmentChips,
      attached_file_count: Math.max(inputFiles, attachmentChips)
    };
  }
  function composerControlKeys(document2) {
    return probeControls(document2).filter((control) => control.region === "composer" && control.visible).map((control) => control.key);
  }
  function composerControlDelta(document2, keysBefore) {
    const remaining = /* @__PURE__ */ new Map();
    for (const key of keysBefore) remaining.set(key, (remaining.get(key) || 0) + 1);
    const addedControls = [];
    for (const control of probeControls(document2)) {
      if (control.region !== "composer" || !control.visible) continue;
      const prior = remaining.get(control.key) || 0;
      if (prior > 0) {
        remaining.set(control.key, prior - 1);
      } else {
        addedControls.push(control);
      }
    }
    return {
      added_keys: addedControls.map((control) => control.key),
      added_controls: addedControls
    };
  }
  function buildSurfaceProbe(document2, inputs) {
    const controls = probeControls(document2);
    const composer = composerState(document2, inputs.composer, controls);
    const authentication = authenticationState(document2);
    const anchors = probeAnchors(
      document2,
      {
        composer: inputs.composer,
        send: inputs.send,
        stop: inputs.stop,
        continue: inputs.continueControl,
        latestAssistant: inputs.latestAssistant,
        latestUser: inputs.latestUser
      },
      { composer: inputs.expectedComposerSelector, send: inputs.expectedSendSelector }
    );
    const oddities = collectOddities(controls, anchors, composer);
    const byRole = {};
    for (const control of controls) {
      byRole[control.classification] = (byRole[control.classification] || 0) + 1;
    }
    return {
      probe_version: SURFACE_PROBE_VERSION,
      captured_at: (/* @__PURE__ */ new Date()).toISOString(),
      url: inputs.url,
      route: inputs.route,
      authentication,
      composer,
      capabilities: {
        // Each of these maps 1:1 onto a GlassTTY command that breaks if it is false.
        write_prompt: Boolean(inputs.composer),
        // null when the composer is empty: ChatGPT hides send until you type, so a
        // missing send button here proves nothing either way. Claiming `false`
        // would flag a healthy page as broken (see the note on `capabilities`).
        submit_prompt: inputs.send ? true : composer.present && composer.empty ? null : false,
        detect_generation: inputs.generationState !== "unknown",
        read_latest_output: Boolean(inputs.latestAssistant),
        read_user_turn: Boolean(inputs.latestUser),
        continue_generation: Boolean(inputs.continueControl),
        attach_files: composer.file_input_present && authentication.posture === "authenticated"
      },
      anchors,
      controls,
      oddities,
      counts: {
        controls: controls.length,
        visible_controls: controls.filter((control) => control.visible).length,
        unknown_controls: controls.filter((control) => control.classification === "unknown").length,
        oddities: oddities.length,
        critical_oddities: oddities.filter((oddity) => oddity.severity === "critical").length,
        ...byRole
      }
    };
  }

  // src/adapters/chatgpt.ts
  var PROMPT_SELECTORS = [
    "#prompt-textarea",
    '[data-testid="prompt-textarea"]',
    'textarea[placeholder*="Message" i]',
    'textarea[placeholder*="Ask" i]',
    "textarea",
    '[contenteditable="true"][role="textbox"]',
    '[contenteditable="plaintext-only"][role="textbox"]',
    '[role="textbox"]',
    'main [data-placeholder*="Message" i]',
    'main [data-placeholder*="Ask" i]',
    "main .ProseMirror[contenteditable]",
    'main [contenteditable="true"]',
    'main [contenteditable="plaintext-only"]',
    '[contenteditable="true"]',
    '[contenteditable="plaintext-only"]'
  ];
  var OUTPUT_SELECTORS = [
    '[data-message-author-role="assistant"]',
    '[data-testid*="conversation-turn"]',
    "article",
    "main article",
    'main [class*="markdown"]',
    ".markdown",
    '[class*="assistant"]',
    '[class*="message"]',
    "main",
    '[role="main"]'
  ];
  var USER_TURN_SELECTORS = [
    '[data-message-author-role="user"]',
    '[data-testid*="conversation-turn"]',
    "article",
    "main article",
    '[class*="user"]',
    '[class*="message"]'
  ];
  var OBSERVED_LIVE_PROMPT_SELECTOR = "#prompt-textarea";
  var OBSERVED_LIVE_SEND_SELECTOR = "#composer-submit-button";
  var OBSERVED_LIVE_SEND_TESTID = "send-button";
  var OBSERVED_LIVE_SEND_ARIA_LABEL = "Send prompt";
  var SEND_BUTTON_SELECTORS = [
    "#composer-submit-button",
    "button#composer-submit-button",
    'button[data-testid="send-button"]',
    'button[aria-label*="Send" i]',
    'button[title*="Send" i]',
    'form button[type="submit"]',
    "button"
  ];
  var SEND_BUTTON_MIN_SCORE = 0.45;
  var GENERATION_STOP_TERMS = [
    "stop generating",
    "stop streaming",
    "stop response",
    "stop responding",
    "stop"
  ];
  var GENERATION_CONTINUE_TERMS = [
    "continue generating",
    "continue response",
    "continue"
  ];
  var NON_SEND_CONTROL_TERMS = [
    "add files",
    "add file",
    "add photos",
    "add photo",
    "add files and more",
    "composer-plus",
    "plus",
    "attach",
    "attachment",
    "upload",
    "file",
    "files",
    "voice",
    "dictate",
    "microphone",
    "audio",
    "stop",
    "cancel",
    "search",
    "tools",
    "tool",
    "deep research",
    "model",
    "picker",
    "reasoning",
    "library",
    "canvas",
    "email",
    "recipient",
    "image",
    "create image",
    "start dictation",
    "copy response",
    "copy message",
    "edit message",
    "good response",
    "bad response",
    "download apps",
    "sources",
    "extra high",
    "prompt 1",
    "prompt 2",
    "prompt 3",
    "prompt 4",
    "prompt 5",
    "prompt 6",
    "prompt 7",
    "prompt 8"
  ];
  var surfaceOverrides = {};
  function setSurfaceOverrides(next) {
    surfaceOverrides = next && typeof next === "object" ? next : {};
  }
  function getSurfaceOverrides() {
    return surfaceOverrides;
  }
  function topContext(document2, win) {
    return inventoryContexts(document2, win)[0];
  }
  function overrideNode(selector, document2) {
    if (!selector) return null;
    let node = null;
    try {
      node = document2.querySelector(selector);
    } catch {
      return null;
    }
    if (!node || !(node instanceof HTMLElement)) return null;
    return isVisible(node) ? node : null;
  }
  function lower2(value) {
    return (value || "").trim().toLowerCase();
  }
  function includesAny(value, terms) {
    return terms.some((term) => value.includes(term));
  }
  function authorRoleElement(node) {
    return node?.closest("[data-message-author-role]") ?? null;
  }
  function authorRole(node) {
    return lower2(authorRoleElement(node)?.getAttribute("data-message-author-role")) || null;
  }
  function authorRoleSource(node) {
    const roleElement = authorRoleElement(node);
    if (!roleElement) return null;
    return roleElement === node ? "self" : "ancestor";
  }
  function contentEditableMode(node) {
    const raw = node.getAttribute("contenteditable");
    if (raw === null) return null;
    const value = lower2(raw);
    if (value === "false") return null;
    return value || "true";
  }
  function isEditableCandidate(node) {
    if (node instanceof HTMLTextAreaElement) return !node.disabled && !node.readOnly;
    if (node instanceof HTMLInputElement) return !node.disabled && !node.readOnly;
    return Boolean(contentEditableMode(node)) || node.getAttribute("role") === "textbox";
  }
  function promptScore(node) {
    let score = isVisible(node) ? 0.45 : 0.03;
    const id = lower2(node.getAttribute("id"));
    const testId = lower2(node.getAttribute("data-testid"));
    const placeholder = lower2(node.getAttribute("placeholder"));
    const dataPlaceholder = lower2(node.getAttribute("data-placeholder"));
    const aria = lower2(node.getAttribute("aria-label"));
    const role = lower2(node.getAttribute("role"));
    const text = lower2(textFrom(node));
    const className = lower2(node.getAttribute("class"));
    if (!isEditableCandidate(node)) score -= 0.35;
    if (id === "prompt-textarea") score += 0.35;
    if (testId.includes("prompt-textarea")) score += 0.35;
    if (node instanceof HTMLTextAreaElement) score += 0.25;
    if (role === "textbox") score += 0.22;
    if (contentEditableMode(node)) score += 0.18;
    if (includesAny(placeholder, ["message", "ask anything", "chatgpt", "prompt"])) score += 0.2;
    if (includesAny(dataPlaceholder, ["message", "ask anything", "chatgpt", "prompt"])) score += 0.2;
    if (includesAny(aria, ["message", "prompt", "ask", "chatgpt"])) score += 0.16;
    if (className.includes("composer") || className.includes("prompt")) score += 0.08;
    if (includesAny(id + " " + testId + " " + placeholder + " " + dataPlaceholder + " " + aria, ["search", "filter", "rename", "title", "email", "recipient"])) score -= 0.28;
    if (text.length > 0 && text.length < 16e3) score += 0.04;
    if (text.length > 24e3) score -= 0.2;
    return score;
  }
  function outputScore(node) {
    const text = textFrom(node) || "";
    let score = isVisible(node) ? 0.35 : 0.04;
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    const role = lower2(node.getAttribute("role"));
    const roleForTurn = authorRole(node);
    if (roleForTurn === "assistant") score += 0.55;
    if (roleForTurn === "user") score -= 0.55;
    if (dataTestId.includes("conversation-turn")) score += 0.18;
    if (node.tagName === "ARTICLE") score += 0.16;
    if (className.includes("markdown")) score += 0.14;
    if (className.includes("assistant")) score += 0.18;
    if (className.includes("message")) score += 0.08;
    if (role === "main") score -= 0.08;
    if (text.length > 30) score += 0.12;
    if (text.length > 250) score += 0.1;
    if (text.length > 5e3) score -= 0.08;
    if (text.length > 2e4) score -= 0.25;
    return score;
  }
  function sendControlSignal(button) {
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const id = lower2(button.getAttribute("id"));
    const type = lower2(button.getAttribute("type"));
    const combined = `${text} ${aria} ${title} ${id} ${testId}`;
    const explicitSendIntent = testId === "send-button" || testId.includes("send-button") || testId.includes("send-message") || id === "composer-submit-button" || id === "send-button" || aria === "send" || aria.includes("send message") || aria.includes("send prompt") || title === "send" || title.includes("send message") || text === "send";
    const formSubmitIntent = type === "submit";
    const nonSendControl = includesAny(combined, NON_SEND_CONTROL_TERMS);
    const exactPlusControl = id === "composer-plus-btn" || testId === "composer-plus-btn";
    return {
      intent: explicitSendIntent || formSubmitIntent,
      explicit: explicitSendIntent,
      submit: formSubmitIntent,
      disqualified: exactPlusControl || nonSendControl && !explicitSendIntent,
      combined
    };
  }
  function userTurnScore(node) {
    const text = textFrom(node) || "";
    let score = isVisible(node) ? 0.34 : 0.03;
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    const role = lower2(node.getAttribute("role"));
    const roleForTurn = authorRole(node);
    if (roleForTurn === "user") score += 0.55;
    if (roleForTurn === "assistant") score -= 0.55;
    if (dataTestId.includes("conversation-turn")) score += 0.16;
    if (node.tagName === "ARTICLE") score += 0.12;
    if (className.includes("user")) score += 0.18;
    if (className.includes("message")) score += 0.06;
    if (roleForTurn === "assistant" || className.includes("assistant")) score -= 0.45;
    if (role === "main") score -= 0.12;
    if (node.matches('textarea, input, [contenteditable="true"], [role="textbox"]')) score -= 0.8;
    if (node.closest('form, [data-testid*="composer"], [class*="composer"]')) score -= 0.5;
    if (text.length > 12) score += 0.08;
    if (text.length > 5e3) score -= 0.16;
    return score;
  }
  function sendButtonScore(button, composer = null) {
    let score = isVisible(button) ? 0.3 : 0.02;
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const type = lower2(button.getAttribute("type"));
    const disabled = button.disabled || button.getAttribute("aria-disabled") === "true";
    const signal = sendControlSignal(button);
    if (disabled) score -= 0.8;
    if (!signal.intent) score -= 0.35;
    if (signal.disqualified) score -= 1;
    if (testId === "send-button" || testId.includes("send")) score += 0.5;
    if (aria === "send" || aria.includes("send message") || aria.includes("send prompt")) score += 0.45;
    if (title === "send" || title.includes("send message")) score += 0.32;
    if (text === "send") score += 0.3;
    if (type === "submit") score += 0.18;
    if (composer) {
      const sameForm = button.form && (composer instanceof HTMLInputElement || composer instanceof HTMLTextAreaElement ? composer.form === button.form : Boolean(composer.closest("form") && composer.closest("form") === button.form));
      const composerRoot = findComposerActionRoot(composer, button.ownerDocument);
      if (sameForm) score += 0.2;
      if (composerRoot !== button.ownerDocument && composerRoot.contains(button)) score += 0.16;
      const buttonDialog = button.closest('dialog, [role="dialog"], [role="alertdialog"]');
      const composerDialog = composer.closest('dialog, [role="dialog"], [role="alertdialog"]');
      if (buttonDialog && buttonDialog !== composerDialog) score -= 0.35;
    } else {
      score -= 0.12;
    }
    if (button.closest("nav, header, aside")) score -= 0.18;
    return score;
  }
  function routePostureAllowsSubmit(posture) {
    return posture === "plain-chat";
  }
  function findComposerActionRoot(composer, document2) {
    if (!composer) return document2;
    return composer.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') || composer.parentElement || document2;
  }
  function inventoryContexts(document2, win) {
    return collectLiveFrameInventory(document2, win).contexts;
  }
  function rank(selectors, document2, scorer, win) {
    const seen = /* @__PURE__ */ new Set();
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      for (const selector of selectors) {
        for (const node of Array.from(context.document.querySelectorAll(selector))) {
          if (seen.has(node)) continue;
          seen.add(node);
          ranked.push({ node, context, index, score: scorer(node) });
          index += 1;
        }
      }
    }
    return ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index);
  }
  function bestVisibleElement(selectors, document2, scorer, win) {
    const best = rank(selectors, document2, scorer, win).find(({ node, score }) => score > 0.35 && node instanceof HTMLElement);
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null
    };
  }
  function findPromptComposer(document2, win) {
    const overridden = overrideNode(surfaceOverrides.composer, document2);
    if (overridden && isEditableCandidate(overridden)) {
      return { node: overridden, context: topContext(document2, win) };
    }
    return bestVisibleElement(PROMPT_SELECTORS, document2, promptScore, win);
  }
  function documentOrderIndex(node) {
    if (!node) return void 0;
    const nodes = Array.from(node.ownerDocument.querySelectorAll("*"));
    const index = nodes.indexOf(node);
    return index >= 0 ? index : void 0;
  }
  function outputDocumentOrder(left, right) {
    if (left.node.ownerDocument !== right.node.ownerDocument) {
      return left.context.depth - right.context.depth || left.index - right.index;
    }
    if (left.node === right.node) return 0;
    const position = left.node.compareDocumentPosition(right.node);
    if (position & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
    if (position & Node.DOCUMENT_POSITION_PRECEDING) return 1;
    return left.index - right.index;
  }
  function isAssistantOutputCandidate(node) {
    const roleForTurn = authorRole(node);
    if (roleForTurn) return roleForTurn === "assistant";
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    return className.includes("assistant") || dataTestId.includes("assistant") || node.tagName === "ARTICLE";
  }
  function isUserTurnCandidate(node) {
    const roleForTurn = authorRole(node);
    if (roleForTurn) return roleForTurn === "user";
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    return className.includes("user") || dataTestId.includes("user") || node.tagName === "ARTICLE";
  }
  function latestOutputMatch(document2, win) {
    const candidates = rank(OUTPUT_SELECTORS, document2, outputScore, win).filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
    const assistantLike = candidates.filter(({ node }) => isAssistantOutputCandidate(node));
    const ordered = (assistantLike.length ? assistantLike : candidates).slice().sort(outputDocumentOrder);
    const best = ordered[ordered.length - 1];
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      assistant_like: Boolean(best && isAssistantOutputCandidate(best.node))
    };
  }
  function findLatestOutputNode(document2, win) {
    const match = latestOutputMatch(document2, win);
    return { node: match.node, context: match.context };
  }
  function latestOutputWitness(document2, win) {
    const match = latestOutputMatch(document2, win);
    const node = match.node;
    const context = match.context;
    const roleForTurn = authorRole(node);
    return {
      text: textFrom(node),
      selector_hint: node ? selectorHint(node, "output") : null,
      selection_policy: "latest-visible-assistant-like-node-in-dom-order",
      assistant_like: match.assistant_like || roleForTurn === "assistant",
      author_role: roleForTurn,
      author_role_source: authorRoleSource(node),
      node_tag: node ? node.tagName.toLowerCase() : null,
      candidate_score: Number(match.score.toFixed(3)),
      ...typeof documentOrderIndex(node) === "number" ? { document_order_index: documentOrderIndex(node) } : {},
      ...typeof context?.depth === "number" ? { frame_depth: context.depth } : {},
      ...context?.frame_path ? { frame_path: context.frame_path } : {}
    };
  }
  function latestUserTurnMatch(document2, win) {
    const candidates = rank(USER_TURN_SELECTORS, document2, userTurnScore, win).filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
    const userLike = candidates.filter(({ node }) => isUserTurnCandidate(node));
    const ordered = (userLike.length ? userLike : candidates).slice().sort(outputDocumentOrder);
    const best = ordered[ordered.length - 1];
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      user_like: Boolean(best && isUserTurnCandidate(best.node))
    };
  }
  function latestUserTurnWitness(document2, win) {
    const match = latestUserTurnMatch(document2, win);
    const node = match.node;
    const context = match.context;
    const roleForTurn = authorRole(node);
    return {
      text: textFrom(node),
      selector_hint: node ? selectorHint(node, "user-turn") : null,
      selection_policy: "latest-visible-user-like-node-in-dom-order",
      user_like: match.user_like || roleForTurn === "user",
      author_role: roleForTurn,
      author_role_source: authorRoleSource(node),
      node_tag: node ? node.tagName.toLowerCase() : null,
      candidate_score: Number(match.score.toFixed(3)),
      ...typeof documentOrderIndex(node) === "number" ? { document_order_index: documentOrderIndex(node) } : {},
      ...typeof context?.depth === "number" ? { frame_depth: context.depth } : {},
      ...context?.frame_path ? { frame_path: context.frame_path } : {}
    };
  }
  function findLikelySendButton(document2, win, composer = null) {
    const overridden = overrideNode(surfaceOverrides.send, document2);
    if (overridden instanceof HTMLButtonElement) {
      const signal = sendControlSignal(overridden);
      if (!signal.disqualified) {
        return { node: overridden, context: topContext(document2, win), score: sendButtonScore(overridden, composer), scope: document2, signal };
      }
    }
    const seen = /* @__PURE__ */ new Set();
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
      const scopedRoot = findComposerActionRoot(contextComposer, context.document);
      const scopes = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
      for (const scope of scopes) {
        for (const selector of SEND_BUTTON_SELECTORS) {
          for (const node of Array.from(scope.querySelectorAll(selector))) {
            if (seen.has(node) || !(node instanceof HTMLButtonElement)) continue;
            seen.add(node);
            ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), scope });
            index += 1;
          }
        }
      }
    }
    const best = ranked.filter(({ button, score }) => {
      const signal = sendControlSignal(button);
      return score > SEND_BUTTON_MIN_SCORE && signal.intent && !signal.disqualified && !button.disabled && button.getAttribute("aria-disabled") !== "true";
    }).sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return {
      node: best?.button ?? null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      scope: best?.scope ?? null,
      signal: best?.button ? sendControlSignal(best.button) : null
    };
  }
  function findBlockedComposerControl(document2, win, composer = null) {
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
      const scopedRoot = findComposerActionRoot(contextComposer, context.document);
      const scopes = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
      for (const scope of scopes) {
        for (const node of Array.from(scope.querySelectorAll("button"))) {
          if (!(node instanceof HTMLButtonElement)) continue;
          const signal = sendControlSignal(node);
          if (!signal.disqualified) continue;
          ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), signal });
          index += 1;
        }
      }
    }
    const best = ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return {
      node: best?.button ?? null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      signal: best?.signal ?? null
    };
  }
  function generationControlScore(button, terms) {
    if (!isVisible(button) || button.disabled || button.getAttribute("aria-disabled") === "true") return 0;
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const combined = `${text} ${aria} ${title} ${testId}`;
    if (!includesAny(combined, terms)) return 0;
    let score = 0.45;
    if (includesAny(aria, terms) || includesAny(title, terms)) score += 0.22;
    if (includesAny(testId, terms.map((term) => term.replace(/\s+/g, "-")))) score += 0.12;
    if (button.closest('main, [role="main"]')) score += 0.08;
    if (button.closest("nav, header, aside")) score -= 0.2;
    return score;
  }
  function findGenerationControl(document2, win, terms) {
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      for (const button of Array.from(context.document.querySelectorAll("button"))) {
        if (!(button instanceof HTMLButtonElement)) continue;
        const score = generationControlScore(button, terms);
        if (score <= 0.35) continue;
        ranked.push({ button, context, index, score });
        index += 1;
      }
    }
    const best = ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return { node: best?.button ?? null, context: best?.context ?? null, score: best?.score ?? 0 };
  }
  function generationState(document2, win) {
    const stop = findGenerationControl(document2, win, GENERATION_STOP_TERMS);
    const continueControl = findGenerationControl(document2, win, GENERATION_CONTINUE_TERMS);
    if (stop.node) return { state: "streaming-or-stoppable", stop, continue: continueControl };
    if (continueControl.node) return { state: "needs-continue", stop, continue: continueControl };
    return { state: "settled-or-idle", stop, continue: continueControl };
  }
  function setNativeValue(node, text) {
    const prototype = Object.getPrototypeOf(node);
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (descriptor?.set) {
      descriptor.set.call(node, text);
    } else {
      node.value = text;
    }
  }
  function dispatchEditableEvents(node, text) {
    node.dispatchEvent(new InputEvent("beforeinput", { bubbles: true, cancelable: true, data: text, inputType: "insertText" }));
    node.dispatchEvent(new InputEvent("input", { bubbles: true, data: text, inputType: "insertText" }));
    node.dispatchEvent(new Event("change", { bubbles: true }));
  }
  function readbackMatches(node, expected) {
    const actual = (textFrom(node) || "").replace(/\s+/g, " ").trim();
    const target = expected.replace(/\s+/g, " ").trim();
    return actual === target;
  }
  function writeIntoElement(node, text) {
    node.focus();
    if (node instanceof HTMLTextAreaElement || node instanceof HTMLInputElement) {
      setNativeValue(node, text);
      dispatchEditableEvents(node, text);
      return readbackMatches(node, text);
    }
    if (contentEditableMode(node) || node.getAttribute("role") === "textbox") {
      const doc = node.ownerDocument;
      const selection = doc.getSelection();
      if (selection) {
        const range = doc.createRange();
        range.selectNodeContents(node);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      let inserted = false;
      try {
        inserted = doc.execCommand("insertText", false, text);
      } catch {
        inserted = false;
      }
      if (!inserted) {
        node.textContent = text;
      }
      dispatchEditableEvents(node, text);
      return readbackMatches(node, text);
    }
    return false;
  }
  function sanitizeHtml(node) {
    if (!node) return null;
    const clone = node.cloneNode(true);
    clone.querySelectorAll("img, svg, button, input, textarea, script, style, video, canvas").forEach((child) => child.remove());
    clone.querySelectorAll("*").forEach((el) => {
      for (const attr of Array.from(el.attributes)) {
        if (!["class", "role", "data-testid", "aria-label", "placeholder", "data-placeholder", "data-message-author-role"].includes(attr.name)) {
          el.removeAttribute(attr.name);
        }
      }
    });
    return (clone.outerHTML || "").replace(/\s+/g, " ").slice(0, 3e3);
  }
  function compactVisibleText(nodes, limit = 2400) {
    return nodes.filter((node) => isVisible(node)).map((node) => textFrom(node) || "").join(" ").replace(/\s+/g, " ").trim().slice(0, limit).toLowerCase();
  }
  function activeShellText(document2) {
    return compactVisibleText(Array.from(document2.querySelectorAll([
      "dialog[open]",
      '[role="dialog"]',
      '[role="alertdialog"]',
      '[aria-modal="true"]',
      'main [aria-current="page"]',
      'main [aria-selected="true"]',
      'main [aria-pressed="true"]',
      'main [data-state="active"]',
      '[data-testid*="composer"] [aria-pressed="true"]',
      '[data-testid*="tools"] [aria-pressed="true"]'
    ].join(","))));
  }
  function classifyRouteDetails(url, document2, win) {
    let pathname = "/";
    try {
      pathname = new URL(url).pathname.toLowerCase();
    } catch {
      pathname = "/";
    }
    const promptPresent = Boolean(findPromptComposer(document2, win).node);
    const evidence = [`path:${pathname}`, promptPresent ? "composer:present" : "composer:missing"];
    const shellText = activeShellText(document2);
    if (includesAny(pathname, ["/auth/", "/login"]) || !promptPresent && includesAny(shellText, ["log in", "sign up", "stay logged out"])) {
      evidence.push("auth-or-marketing-signal");
      return { posture: "login-or-marketing", pathname, prompt_present: promptPresent, evidence };
    }
    if (pathname === "/" || pathname.startsWith("/c/")) {
      if (promptPresent) {
        evidence.push("plain-chat-path-and-composer");
        return { posture: "plain-chat", pathname, prompt_present: promptPresent, evidence };
      }
    }
    if (includesAny(pathname, ["/agent", "/tasks", "/task/"])) {
      evidence.push("agent-or-task-path");
      return { posture: "agent-or-tool", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(pathname, ["/canvas", "/artifact"])) {
      evidence.push("canvas-or-artifact-path");
      return { posture: "canvas-or-artifact", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(pathname, ["/g/", "/gpts", "/project", "/projects"])) {
      evidence.push("project-or-gpt-path");
      return { posture: "project-or-gpt", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["agent mode", "take over", "browser task"])) {
      evidence.push("active-agent-shell-signal");
      return { posture: "agent-or-tool", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["canvas", "artifact"])) {
      evidence.push("active-canvas-shell-signal");
      return { posture: "canvas-or-artifact", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["gpt builder", "custom gpt", "project settings"])) {
      evidence.push("active-project-shell-signal");
      return { posture: "project-or-gpt", pathname, prompt_present: promptPresent, evidence };
    }
    if (promptPresent) {
      evidence.push("composer-present-no-blocking-route-signal");
      return { posture: "plain-chat", pathname, prompt_present: promptPresent, evidence };
    }
    evidence.push("no-supported-route-signal");
    return { posture: "unknown", pathname, prompt_present: promptPresent, evidence };
  }
  function matchChatGptDocument(url, document2) {
    try {
      const parsed = new URL(url);
      if (parsed.hostname !== "chatgpt.com" && !parsed.hostname.endsWith(".chatgpt.com")) return false;
    } catch {
      return false;
    }
    return Boolean(document2);
  }
  var chatgptAdapter = {
    name: "chatgpt",
    origin_patterns: ["https://chatgpt.com/"],
    capabilities: {
      read_prompt: true,
      write_prompt: true,
      submit_prompt: true,
      read_latest_output: true,
      read_selection: true,
      debug_candidates: true,
      fixture_capture: true,
      generation_state: true,
      continue_generation: true,
      surface_probe: true,
      attach_files: true
    },
    matches(url, document2) {
      return matchChatGptDocument(url, document2);
    },
    readPrompt(document2) {
      return textFrom(findPromptComposer(document2, window).node);
    },
    writePrompt(document2, text) {
      const node = findPromptComposer(document2, window).node;
      if (!node) return false;
      return writeIntoElement(node, text);
    },
    readLatestOutput(document2) {
      return latestOutputWitness(document2, window).text;
    },
    readLatestOutputWitness(document2) {
      return latestOutputWitness(document2, window);
    },
    readLatestUserTurnWitness(document2) {
      return latestUserTurnWitness(document2, window);
    },
    readSelection(window2) {
      return window2.getSelection()?.toString().trim() || null;
    },
    debugCandidates(document2) {
      const inputs = rank(PROMPT_SELECTORS, document2, promptScore, window).slice(0, 16).map(({ node, context }) => candidateInfo(node, promptScore(node), "prompt", context.window)).sort((a, b) => b.score - a.score);
      const outputs = rank(OUTPUT_SELECTORS, document2, outputScore, window).slice(0, 16).map(({ node, context }) => candidateInfo(node, outputScore(node), "output", context.window)).sort((a, b) => b.score - a.score);
      return { inputs, outputs };
    },
    captureFixture(document2, window2) {
      const inventory = collectLiveFrameInventory(document2, window2);
      const promptMatch = findPromptComposer(document2, window2);
      const outputWitness = latestOutputWitness(document2, window2);
      const userTurnWitness = latestUserTurnWitness(document2, window2);
      const outputMatch = latestOutputMatch(document2, window2);
      const submitMatch = findLikelySendButton(document2, window2, promptMatch.node);
      const blockedControl = findBlockedComposerControl(document2, window2, promptMatch.node);
      const debug = this.debugCandidates(document2);
      const route = classifyRouteDetails(window2.location.href, document2, window2);
      const generation = generationState(document2, window2);
      const submitCandidate = submitMatch.node && submitMatch.context ? candidateInfo(submitMatch.node, submitMatch.score || 1, "button", submitMatch.context.window) : null;
      const blockedCandidate = blockedControl.node && blockedControl.context ? candidateInfo(blockedControl.node, blockedControl.score || 1, "blocked-composer-control", blockedControl.context.window) : null;
      const stopCandidate = generation.stop.node && generation.stop.context ? candidateInfo(generation.stop.node, generation.stop.score || 1, "generation-stop", generation.stop.context.window) : null;
      const continueCandidate = generation.continue.node && generation.continue.context ? candidateInfo(generation.continue.node, generation.continue.score || 1, "generation-continue", generation.continue.context.window) : null;
      return {
        adapter: "chatgpt",
        url: window2.location.href,
        title: document2.title,
        prompt: this.readPrompt(document2),
        latest_output: outputWitness.text,
        latest_output_witness: outputWitness,
        latest_user_turn_witness: userTurnWitness,
        selection: this.readSelection(window2),
        candidates: debug,
        html_samples: {
          prompt: sanitizeHtml(promptMatch.node),
          latest_output: sanitizeHtml(outputMatch.node),
          submit: sanitizeHtml(submitMatch.node)
        },
        metadata: {
          surface_route: route.pathname,
          route_posture: route.posture,
          route_evidence: route.evidence,
          route_prompt_present: route.prompt_present,
          prompt_selector: promptMatch.node ? selectorHint(promptMatch.node, "prompt") : null,
          latest_output_selector: outputWitness.selector_hint,
          latest_output_order_policy: outputWitness.selection_policy,
          latest_output_assistant_like: outputWitness.assistant_like,
          latest_output_author_role: outputWitness.author_role,
          latest_output_author_role_source: outputWitness.author_role_source,
          latest_output_candidate_score: outputWitness.candidate_score,
          latest_output_document_order_index: outputWitness.document_order_index,
          latest_user_turn_selector: userTurnWitness.selector_hint,
          latest_user_turn_order_policy: userTurnWitness.selection_policy,
          latest_user_turn_user_like: userTurnWitness.user_like,
          latest_user_turn_author_role: userTurnWitness.author_role,
          latest_user_turn_author_role_source: userTurnWitness.author_role_source,
          latest_user_turn_candidate_score: userTurnWitness.candidate_score,
          latest_user_turn_document_order_index: userTurnWitness.document_order_index,
          latest_turn_pair_same_frame: Boolean(outputWitness.frame_path && userTurnWitness.frame_path && outputWitness.frame_path === userTurnWitness.frame_path),
          latest_turn_pair_user_before_assistant: typeof userTurnWitness.document_order_index === "number" && typeof outputWitness.document_order_index === "number" ? userTurnWitness.document_order_index < outputWitness.document_order_index : false,
          generation_state: generation.state,
          generation_stop_control_present: Boolean(generation.stop.node),
          generation_continue_control_present: Boolean(generation.continue.node),
          generation_stop_selector: generation.stop.node ? selectorHint(generation.stop.node, "generation-stop") : null,
          generation_continue_selector: generation.continue.node ? selectorHint(generation.continue.node, "generation-continue") : null,
          generation_stop_score: generation.stop.score,
          generation_continue_score: generation.continue.score,
          submit_selector: submitMatch.node ? selectorHint(submitMatch.node, "button") : null,
          submit_score: submitMatch.score,
          submit_signal_intent: submitMatch.signal?.intent ?? false,
          submit_signal_explicit: submitMatch.signal?.explicit ?? false,
          submit_signal_submit_type: submitMatch.signal?.submit ?? false,
          submit_signal_disqualified: submitMatch.signal?.disqualified ?? false,
          observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
          observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
          observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
          submit_expected_live_selector: OBSERVED_LIVE_SEND_SELECTOR,
          blocked_composer_control_selector: blockedControl.node ? selectorHint(blockedControl.node, "blocked-composer-control") : null,
          blocked_composer_control_score: blockedControl.score,
          blocked_composer_control_disqualified: blockedControl.signal?.disqualified ?? false,
          submit_scope_selector: submitMatch.scope && submitMatch.scope !== document2 && submitMatch.scope instanceof Element ? selectorHint(submitMatch.scope, "submit-scope") : null,
          action_policy: {
            submit_method: "button-click-only",
            keyboard_submit_enabled: false,
            route_posture_allows_submit: routePostureAllowsSubmit(route.posture),
            prompt_present_for_submit: Boolean(this.readPrompt(document2)),
            submit_button_found: Boolean(submitMatch.node),
            submit_button_min_score: SEND_BUTTON_MIN_SCORE,
            submit_button_requires_explicit_send_intent: true,
            submit_button_rejects_non_send_composer_controls: true,
            observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
            observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
            observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
            submit_button_live_surface_lock: "#composer-submit-button[data-testid=send-button]",
            blocked_composer_plus_control_present: Boolean(blockedControl.node),
            empty_composer_missing_send_is_allowed: true
          },
          ...buildLiveFixtureMetadata(document2, promptMatch.node, submitMatch.node, debug.inputs[0] ?? null, submitCandidate, {
            inventory,
            inputCandidates: debug.inputs,
            outputCandidates: debug.outputs,
            submitCandidates: [submitCandidate, blockedCandidate, stopCandidate, continueCandidate].filter((candidate) => Boolean(candidate))
          })
        }
      };
    },
    submitPrompt(document2) {
      const route = classifyRouteDetails(window.location.href, document2, window);
      if (!routePostureAllowsSubmit(route.posture)) return false;
      const composer = findPromptComposer(document2, window).node;
      if (!composer || !this.readPrompt(document2)) return false;
      const sendish = findLikelySendButton(document2, window, composer).node;
      if (!sendish) return false;
      composer.focus();
      sendish.click();
      return true;
    },
    generationSnapshot(document2, win) {
      const generation = generationState(document2, win);
      return {
        state: generation.state,
        stop_present: Boolean(generation.stop.node),
        continue_present: Boolean(generation.continue.node),
        stop_selector: generation.stop.node ? selectorHint(generation.stop.node, "generation-stop") : null,
        continue_selector: generation.continue.node ? selectorHint(generation.continue.node, "generation-continue") : null
      };
    },
    continueGeneration(document2, win) {
      const control = findGenerationControl(document2, win, GENERATION_CONTINUE_TERMS);
      if (!control.node) return false;
      control.node.click();
      return true;
    },
    attachmentReadiness(document2) {
      const authentication = authenticationState(document2);
      if (authentication.posture !== "authenticated") {
        return {
          ok: false,
          error: authentication.posture === "anonymous" ? "ChatGPT is logged out; file attachment requires an authenticated browser session" : "ChatGPT authentication could not be verified; refusing to transfer a file",
          authentication: authentication.posture
        };
      }
      const input = findFileInput(document2);
      if (!input) {
        return {
          ok: false,
          error: 'no <input type="file"> found in the page',
          authentication: authentication.posture
        };
      }
      return {
        ok: true,
        input_selector: selectorHint(input, "file-input"),
        authentication: authentication.posture
      };
    },
    /**
     * Put files into the composer.
     *
     * We do NOT click "Add files and more" and drive a native file picker — a page
     * cannot script an OS dialog, and trying is how automation projects end up
     * shipping fragile robot-mouse code. Instead we write straight into the hidden
     * <input type="file"> with a synthetic DataTransfer, which is exactly what the
     * drop handler does.
     */
    attachFiles(document2, files) {
      const readiness = this.attachmentReadiness?.(document2);
      if (!readiness?.ok) {
        return {
          ok: false,
          error: readiness?.error || "file attachment is not available",
          files_before: 0,
          files_after: 0
        };
      }
      const input = findFileInput(document2);
      if (!input) {
        return { ok: false, error: 'no <input type="file"> found in the page', files_before: 0, files_after: 0 };
      }
      const filesBefore = input.files?.length ?? 0;
      try {
        const transfer = new DataTransfer();
        for (const existing of Array.from(input.files ?? [])) transfer.items.add(existing);
        for (const file of files) {
          if (!file.bytes || file.bytes.byteLength === 0) {
            return { ok: false, error: `refusing to attach zero-byte file: ${file.name}`, files_before: filesBefore, files_after: filesBefore };
          }
          const blob = new Blob([file.bytes], { type: file.mime || "application/octet-stream" });
          transfer.items.add(new File([blob], file.name, { type: file.mime || "application/octet-stream" }));
        }
        input.files = transfer.files;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.dispatchEvent(new Event("change", { bubbles: true }));
      } catch (error) {
        return {
          ok: false,
          error: `could not populate file input: ${error instanceof Error ? error.message : String(error)}`,
          files_before: filesBefore,
          files_after: input.files?.length ?? 0
        };
      }
      return {
        ok: true,
        input_selector: selectorHint(input, "file-input"),
        files_before: filesBefore,
        files_after: input.files?.length ?? 0
      };
    },
    clearAttachments(document2) {
      const inputs = findFileInputs(document2);
      if (!inputs.length) {
        return {
          ok: false,
          error: 'no <input type="file"> found in the page',
          inputs_seen: 0,
          files_before: 0,
          files_after: 0
        };
      }
      const filesBefore = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
      try {
        for (const input of inputs) {
          input.files = new DataTransfer().files;
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
      } catch (error) {
        return {
          ok: false,
          error: `could not clear file input: ${error instanceof Error ? error.message : String(error)}`,
          inputs_seen: inputs.length,
          files_before: filesBefore,
          files_after: inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0)
        };
      }
      const filesAfter = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
      return {
        ok: filesAfter === 0,
        inputs_seen: inputs.length,
        files_before: filesBefore,
        files_after: filesAfter
      };
    },
    composerKeys(document2) {
      return composerControlKeys(document2);
    },
    attachmentWitness(document2, keysBefore, expectedName = "", expectedNameVisibleBefore = false) {
      const inputs = findFileInputs(document2);
      const delta = composerControlDelta(document2, keysBefore);
      const added = delta.added_keys;
      const addedControls = delta.added_controls;
      const knownChipKeys = addedControls.filter((control) => control.classification === "attachment-chip").map((control) => control.key);
      const input = inputs[0] ?? null;
      const composerRegion = input?.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') ?? null;
      const expectedNameVisible = Boolean(
        expectedName && composerRegion && (textFrom(composerRegion) || "").toLocaleLowerCase().includes(expectedName.toLocaleLowerCase())
      );
      const expectedNameNewlyVisible = expectedNameVisible && !expectedNameVisibleBefore;
      return {
        input_files: inputs.reduce((count, candidate) => count + (candidate.files?.length ?? 0), 0),
        added_keys: added,
        added_controls: addedControls,
        known_chip_keys: knownChipKeys,
        expected_name_visible: expectedNameVisible,
        expected_name_newly_visible: expectedNameNewlyVisible,
        // A new unrelated control is not an attachment witness. Before the live
        // chip is in the role atlas, require the uploaded filename to be visible
        // in the same composer as the new control.
        chip_present: knownChipKeys.length > 0 || added.length > 0 && expectedNameNewlyVisible
      };
    },
    stopGeneration(document2, win) {
      const control = findGenerationControl(document2, win, GENERATION_STOP_TERMS);
      if (!control.node) return false;
      control.node.click();
      return true;
    },
    newChat(document2) {
      const button = document2.querySelector('[data-testid="create-new-chat-button"]');
      if (button instanceof HTMLElement && isVisible(button)) {
        button.click();
        return true;
      }
      return false;
    },
    surfaceProbe(document2, win) {
      const route = classifyRouteDetails(win.location.href, document2, win);
      const composer = findPromptComposer(document2, win).node;
      const send = findLikelySendButton(document2, win, composer).node;
      const generation = generationState(document2, win);
      const assistant = findLatestOutputNode(document2, win).node;
      const user = latestUserTurnMatch(document2, win).node;
      return buildSurfaceProbe(document2, {
        url: win.location.href,
        route: { pathname: route.pathname, posture: route.posture },
        composer,
        send,
        stop: generation.stop.node,
        continueControl: generation.continue.node,
        latestAssistant: assistant,
        latestUser: user,
        expectedComposerSelector: OBSERVED_LIVE_PROMPT_SELECTOR,
        expectedSendSelector: OBSERVED_LIVE_SEND_SELECTOR,
        generationState: generation.state
      });
    }
  };

  // src/adapters/index.ts
  var adapters = [chatgptAdapter];
  function detectAdapter(url, document2) {
    for (const adapter2 of adapters) {
      if (adapter2.matches(url, document2)) return adapter2;
    }
    return null;
  }

  // src/shared/protocol.ts
  function makeEnvelope(type, payload, tab_id) {
    return {
      version: "0.1",
      request_id: crypto.randomUUID(),
      type,
      tab_id,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      payload
    };
  }
  function replyTo(request, type, payload, tab_id) {
    return {
      version: "0.1",
      request_id: request.request_id,
      type,
      tab_id: tab_id ?? request.tab_id,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      payload
    };
  }

  // src/content/main.ts
  var adapter = detectAdapter(window.location.href, document);
  var lastTranscript = "";
  var transcriptObserver = null;
  var adapterWatcher = null;
  var lastAdapterName = adapter?.name ?? null;
  var lastAdapterUrl = window.location.href;
  var globalScope = globalThis;
  var CONTENT_BOOTSTRAP_VERSION = "rev0059";
  var SURFACE_OVERRIDES_KEY = "glasstty_surface_overrides";
  var attachTransfers = /* @__PURE__ */ new Map();
  var ATTACH_CHUNK_BYTES = 384 * 1024;
  var MAX_ACTIVE_ATTACH_TRANSFERS = 4;
  var MAX_ATTACH_CHUNKS = 4096;
  var MAX_ATTACHMENT_BYTES = 512 * 1024 * 1024;
  var MAX_ATTACH_CHUNK_BASE64 = 4 * Math.ceil(ATTACH_CHUNK_BYTES / 3);
  var ATTACH_TRANSFER_TTL_MS = 30 * 60 * 1e3;
  function pruneAttachTransfers(now = Date.now()) {
    for (const [transferId, transfer] of attachTransfers) {
      if (now - transfer.created_at > ATTACH_TRANSFER_TTL_MS) attachTransfers.delete(transferId);
    }
  }
  function decodeAttachmentChunks(chunks, expectedSize) {
    const out = new Uint8Array(expectedSize);
    let offset = 0;
    for (let index = 0; index < chunks.length; index += 1) {
      const encoded = chunks[index];
      if (encoded === void 0) throw new Error(`attachment chunk ${index} is missing`);
      const binary = atob(encoded);
      if (offset + binary.length > expectedSize) throw new Error("decoded attachment exceeds declared size");
      for (let byteIndex = 0; byteIndex < binary.length; byteIndex += 1) {
        out[offset + byteIndex] = binary.charCodeAt(byteIndex);
      }
      offset += binary.length;
      chunks[index] = void 0;
    }
    if (offset !== expectedSize) throw new Error(`decoded attachment has ${offset} bytes, expected ${expectedSize}`);
    return out;
  }
  function loadSurfaceOverrides() {
    chrome.storage.local.get(SURFACE_OVERRIDES_KEY).then((stored) => {
      const value = stored?.[SURFACE_OVERRIDES_KEY];
      if (value && typeof value === "object") setSurfaceOverrides(value);
    }).catch(() => void 0);
  }
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== "local" || !(SURFACE_OVERRIDES_KEY in changes)) return;
    const next = changes[SURFACE_OVERRIDES_KEY]?.newValue;
    setSurfaceOverrides(next && typeof next === "object" ? next : {});
    log("surface overrides updated", next);
  });
  function log(...args) {
    console.log("[GlassTTY content]", ...args);
  }
  function markDocument() {
    if (!adapter) {
      document.documentElement.removeAttribute("data-glasstty-adapter");
      return;
    }
    document.documentElement.setAttribute("data-glasstty-adapter", adapter.name);
  }
  function sendAdapterDetected() {
    if (!adapter) return;
    chrome.runtime.sendMessage(makeEnvelope("adapter.detected", {
      adapter: adapter.name,
      url: window.location.href
    }));
  }
  function attemptIdFromMessage(message) {
    const payload = message.payload;
    const raw = payload?.attempt_id ?? payload?.attemptId ?? payload?.run_id ?? payload?.runId;
    return typeof raw === "string" && raw.trim() ? raw.trim() : void 0;
  }
  function withAttemptMetadata(payload, attemptId) {
    if (!attemptId) return payload;
    const record = payload;
    const metadata = typeof record.metadata === "object" && record.metadata !== null && !Array.isArray(record.metadata) ? { ...record.metadata, attempt_id: attemptId } : { attempt_id: attemptId };
    return { ...record, attempt_id: attemptId, metadata };
  }
  function resolveAdapter(reason = "resolve") {
    const next = detectAdapter(window.location.href, document);
    const nextName = next?.name ?? null;
    const urlChanged = window.location.href !== lastAdapterUrl;
    const adapterChanged = nextName !== lastAdapterName;
    adapter = next;
    if (globalScope.__glassttyContentBootstrap) {
      globalScope.__glassttyContentBootstrap.adapterName = adapter?.name;
    }
    markDocument();
    if (adapterChanged || urlChanged) {
      log(adapter ? "adapter detected" : "no adapter matched", { adapter: adapter?.name ?? null, reason, url: window.location.href });
      lastAdapterName = nextName;
      lastAdapterUrl = window.location.href;
      lastTranscript = "";
      sendAdapterDetected();
      if (adapter) startTranscriptObserver();
    }
    return adapter;
  }
  function startTranscriptObserver() {
    if (transcriptObserver) return;
    const emit = () => {
      const activeAdapter = resolveAdapter("transcript");
      if (!activeAdapter) return;
      const latest = activeAdapter.readLatestOutput(document) || "";
      if (!latest || latest === lastTranscript) return;
      lastTranscript = latest;
      chrome.runtime.sendMessage(makeEnvelope("transcript.delta", {
        adapter: activeAdapter.name,
        text: latest,
        length: latest.length,
        url: window.location.href
      }));
    };
    emit();
    transcriptObserver = new MutationObserver(() => {
      window.setTimeout(emit, 50);
    });
    if (document.body) {
      transcriptObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
  }
  function startAdapterWatcher() {
    if (adapterWatcher) return;
    const sync = () => window.setTimeout(() => resolveAdapter("dom-or-route-change"), 50);
    adapterWatcher = new MutationObserver(sync);
    if (document.body) {
      adapterWatcher.observe(document.body, { childList: true, subtree: true });
    }
    const history = window.history;
    if (!history.__glassttyPatched) {
      const wrap = (name) => {
        const original = history[name];
        history[name] = function patchedHistoryMethod(...args) {
          const result = original.apply(history, args);
          sync();
          return result;
        };
      };
      wrap("pushState");
      wrap("replaceState");
      history.__glassttyPatched = true;
    }
    window.addEventListener("popstate", sync, { passive: true });
    window.addEventListener("hashchange", sync, { passive: true });
    window.setInterval(() => resolveAdapter("periodic"), 2e3);
  }
  function installRuntimeLane() {
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      const activeAdapter = resolveAdapter(`message:${message.type}`);
      if (!activeAdapter) {
        sendResponse(replyTo(message, "error.report", { error: "no adapter matched current page", url: window.location.href }));
        return true;
      }
      const attemptId = attemptIdFromMessage(message);
      switch (message.type) {
        case "prompt.read":
          sendResponse(replyTo(message, "prompt.read", withAttemptMetadata({ text: activeAdapter.readPrompt(document), adapter: activeAdapter.name, url: window.location.href }, attemptId)));
          return true;
        case "prompt.write":
          sendResponse(replyTo(message, "prompt.write", withAttemptMetadata({ ok: activeAdapter.writePrompt(document, String(message.payload?.text ?? "")), adapter: activeAdapter.name, readback: activeAdapter.readPrompt(document), url: window.location.href }, attemptId)));
          return true;
        case "prompt.submit": {
          const promptBeforeSubmit = activeAdapter.readPrompt(document);
          const ok = activeAdapter.submitPrompt?.(document) ?? false;
          const promptAfterSubmit = activeAdapter.readPrompt(document);
          sendResponse(replyTo(message, "prompt.submit", withAttemptMetadata({
            ok,
            adapter: activeAdapter.name,
            url: window.location.href,
            prompt_before_submit: promptBeforeSubmit,
            composer_readback_before_submit: promptBeforeSubmit,
            submitted_prompt: promptBeforeSubmit,
            prompt_after_submit: promptAfterSubmit
          }, attemptId)));
          return true;
        }
        case "transcript.latest": {
          const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
          const latestUserTurnWitness2 = activeAdapter.readLatestUserTurnWitness?.(document);
          sendResponse(replyTo(message, "transcript.latest", withAttemptMetadata({
            text: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
            latest_output_witness: latestWitness,
            latest_user_turn_witness: latestUserTurnWitness2,
            adapter: activeAdapter.name,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "selection.read":
          sendResponse(replyTo(message, "selection.read", withAttemptMetadata({ text: activeAdapter.readSelection(window), adapter: activeAdapter.name, url: window.location.href }, attemptId)));
          return true;
        case "debug.dom_candidates":
          sendResponse(replyTo(message, "debug.dom_candidates", withAttemptMetadata({ ...activeAdapter.debugCandidates(document), adapter: activeAdapter.name }, attemptId)));
          return true;
        case "fixture.capture":
          sendResponse(replyTo(message, "fixture.capture", withAttemptMetadata(activeAdapter.captureFixture ? activeAdapter.captureFixture(document, window) : {
            adapter: activeAdapter.name,
            url: window.location.href,
            title: document.title,
            prompt: activeAdapter.readPrompt(document),
            latest_output: activeAdapter.readLatestOutput(document),
            selection: activeAdapter.readSelection(window),
            candidates: activeAdapter.debugCandidates(document)
          }, attemptId)));
          return true;
        case "state.snapshot": {
          const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
          const latestUserTurnWitness2 = activeAdapter.readLatestUserTurnWitness?.(document);
          const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
          sendResponse(replyTo(message, "state.snapshot", withAttemptMetadata({
            adapter: activeAdapter.name,
            prompt: activeAdapter.readPrompt(document),
            latest_output: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
            latest_output_witness: latestWitness,
            latest_user_turn_witness: latestUserTurnWitness2,
            generation,
            selection: activeAdapter.readSelection(window),
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "generation.state": {
          const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
          const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
          sendResponse(replyTo(message, "generation.state", withAttemptMetadata({
            adapter: activeAdapter.name,
            generation,
            latest_output: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "attach.begin": {
          const payload = message.payload;
          pruneAttachTransfers();
          const valid = typeof payload.transfer_id === "string" && payload.transfer_id.length > 0 && payload.transfer_id.length <= 128 && typeof payload.name === "string" && payload.name.length > 0 && payload.name.length <= 1024 && Number.isSafeInteger(payload.size) && payload.size > 0 && payload.size <= MAX_ATTACHMENT_BYTES && Number.isSafeInteger(payload.chunks) && payload.chunks > 0 && payload.chunks <= MAX_ATTACH_CHUNKS && payload.chunks === Math.ceil(payload.size / ATTACH_CHUNK_BYTES);
          if (!valid) {
            sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
              ok: false,
              error: `invalid attachment envelope (max ${MAX_ATTACHMENT_BYTES} bytes / ${MAX_ATTACH_CHUNKS} chunks)`
            }, attemptId)));
            return true;
          }
          if (attachTransfers.has(payload.transfer_id)) {
            sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
              ok: false,
              error: "duplicate transfer_id"
            }, attemptId)));
            return true;
          }
          if (attachTransfers.size >= MAX_ACTIVE_ATTACH_TRANSFERS) {
            sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
              ok: false,
              error: `too many active attachment transfers (max ${MAX_ACTIVE_ATTACH_TRANSFERS})`
            }, attemptId)));
            return true;
          }
          const readiness = activeAdapter.attachmentReadiness?.(document) ?? { ok: false, error: "adapter cannot preflight file attachments" };
          if (!readiness.ok) {
            sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
              ...readiness,
              adapter: activeAdapter.name,
              url: window.location.href
            }, attemptId)));
            return true;
          }
          const composerKeysBefore = activeAdapter.composerKeys?.(document) ?? [];
          const witnessBefore = activeAdapter.attachmentWitness?.(
            document,
            composerKeysBefore,
            payload.name,
            false
          ) ?? null;
          const rawInputFilesBefore = witnessBefore?.input_files;
          if (typeof rawInputFilesBefore !== "number" || !Number.isSafeInteger(rawInputFilesBefore) || rawInputFilesBefore < 0) {
            sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
              ok: false,
              error: "adapter did not return a valid pre-transfer attachment count",
              adapter: activeAdapter.name,
              url: window.location.href
            }, attemptId)));
            return true;
          }
          const inputFilesBefore = rawInputFilesBefore;
          const absoluteWitnessBefore = activeAdapter.attachmentWitness?.(document, [], "", false) ?? null;
          const knownChipKeysBefore = Array.isArray(absoluteWitnessBefore?.known_chip_keys) ? absoluteWitnessBefore.known_chip_keys : [];
          const expectedNameVisibleBefore = Boolean(witnessBefore?.expected_name_visible);
          attachTransfers.set(payload.transfer_id, {
            name: payload.name,
            mime: payload.mime || "application/octet-stream",
            size: payload.size,
            chunks: new Array(payload.chunks),
            received: 0,
            // Snapshot the composer BEFORE the file lands, so the chip that appears
            // afterwards is detectable as a diff rather than a guessed selector.
            composer_keys_before: composerKeysBefore,
            input_files_before: inputFilesBefore,
            known_chip_keys_before: knownChipKeysBefore,
            expected_name_visible_before: expectedNameVisibleBefore,
            created_at: Date.now()
          });
          sendResponse(replyTo(message, "attach.begin", withAttemptMetadata({
            ...readiness,
            ok: true,
            adapter: activeAdapter.name,
            transfer_id: payload.transfer_id,
            composer_keys_before: composerKeysBefore,
            input_files_before: inputFilesBefore,
            known_chip_keys_before: knownChipKeysBefore,
            expected_name_visible_before: expectedNameVisibleBefore,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "attach.chunk": {
          const payload = message.payload;
          pruneAttachTransfers();
          const transfer = attachTransfers.get(payload.transfer_id);
          if (!transfer) {
            sendResponse(replyTo(message, "attach.chunk", withAttemptMetadata({ ok: false, error: "unknown transfer_id (did the page reload mid-transfer?)" }, attemptId)));
            return true;
          }
          if (!Number.isSafeInteger(payload.index) || payload.index < 0 || payload.index >= transfer.chunks.length) {
            sendResponse(replyTo(message, "attach.chunk", withAttemptMetadata({
              ok: false,
              error: `chunk index ${String(payload.index)} is outside 0..${transfer.chunks.length - 1}`
            }, attemptId)));
            return true;
          }
          if (typeof payload.data !== "string" || payload.data.length === 0 || payload.data.length > MAX_ATTACH_CHUNK_BASE64) {
            sendResponse(replyTo(message, "attach.chunk", withAttemptMetadata({
              ok: false,
              error: `invalid base64 chunk payload (max ${MAX_ATTACH_CHUNK_BASE64} characters)`
            }, attemptId)));
            return true;
          }
          if (transfer.chunks[payload.index] === void 0) transfer.received += 1;
          transfer.chunks[payload.index] = payload.data;
          sendResponse(replyTo(message, "attach.chunk", withAttemptMetadata({
            ok: true,
            transfer_id: payload.transfer_id,
            index: payload.index,
            received: transfer.received,
            expected: transfer.chunks.length
          }, attemptId)));
          return true;
        }
        case "attach.commit": {
          const payload = message.payload;
          pruneAttachTransfers();
          const transfer = attachTransfers.get(payload.transfer_id);
          if (!transfer) {
            sendResponse(replyTo(message, "attach.commit", withAttemptMetadata({ ok: false, error: "unknown transfer_id" }, attemptId)));
            return true;
          }
          if (transfer.received !== transfer.chunks.length || transfer.chunks.some((chunk) => chunk === void 0)) {
            sendResponse(replyTo(message, "attach.commit", withAttemptMetadata({
              ok: false,
              error: `incomplete transfer: ${transfer.received}/${transfer.chunks.length} chunks`
            }, attemptId)));
            return true;
          }
          attachTransfers.delete(payload.transfer_id);
          const witnessBeforeCommit = activeAdapter.attachmentWitness?.(
            document,
            transfer.composer_keys_before,
            transfer.name,
            transfer.expected_name_visible_before
          ) ?? null;
          const absoluteWitnessBeforeCommit = activeAdapter.attachmentWitness?.(document, [], "", false) ?? null;
          const knownChipKeysBeforeCommit = Array.isArray(absoluteWitnessBeforeCommit?.known_chip_keys) ? absoluteWitnessBeforeCommit.known_chip_keys : [];
          if (witnessBeforeCommit?.input_files !== transfer.input_files_before || JSON.stringify(knownChipKeysBeforeCommit) !== JSON.stringify(transfer.known_chip_keys_before)) {
            sendResponse(replyTo(message, "attach.commit", withAttemptMetadata({
              ok: false,
              error: "composer attachments changed during transfer; refusing to overwrite concurrent operator state",
              composer_keys_before: transfer.composer_keys_before,
              input_files_before: transfer.input_files_before,
              known_chip_keys_before: transfer.known_chip_keys_before,
              expected_name_visible_before: transfer.expected_name_visible_before
            }, attemptId)));
            return true;
          }
          let bytes;
          try {
            bytes = decodeAttachmentChunks(transfer.chunks, transfer.size);
          } catch (error) {
            sendResponse(replyTo(message, "attach.commit", withAttemptMetadata({
              ok: false,
              error: `attachment decode failed: ${error instanceof Error ? error.message : String(error)}`
            }, attemptId)));
            return true;
          }
          const result = activeAdapter.attachFiles?.(document, [{ name: transfer.name, mime: transfer.mime, bytes }]) ?? { ok: false, error: "adapter cannot attach files", files_before: 0, files_after: 0 };
          const witness = activeAdapter.attachmentWitness?.(
            document,
            transfer.composer_keys_before,
            transfer.name,
            transfer.expected_name_visible_before
          ) ?? null;
          sendResponse(replyTo(message, "attach.commit", withAttemptMetadata({
            ...result,
            adapter: activeAdapter.name,
            name: transfer.name,
            bytes: bytes.byteLength,
            composer_keys_before: transfer.composer_keys_before,
            input_files_before: transfer.input_files_before,
            known_chip_keys_before: transfer.known_chip_keys_before,
            expected_name_visible_before: transfer.expected_name_visible_before,
            witness,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "attach.status": {
          const payload = message.payload;
          const witness = activeAdapter.attachmentWitness?.(
            document,
            payload?.composer_keys_before ?? [],
            payload?.expected_name ?? "",
            payload?.expected_name_visible_before ?? false
          ) ?? null;
          sendResponse(replyTo(message, "attach.status", withAttemptMetadata({
            ok: true,
            adapter: activeAdapter.name,
            witness,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "attach.abort": {
          const payload = message.payload;
          const aborted = typeof payload?.transfer_id === "string" && attachTransfers.delete(payload.transfer_id);
          sendResponse(replyTo(message, "attach.abort", withAttemptMetadata({
            ok: true,
            aborted,
            adapter: activeAdapter.name
          }, attemptId)));
          return true;
        }
        case "attach.clear": {
          const payload = message.payload;
          const result = activeAdapter.clearAttachments?.(document) ?? { ok: false, error: "adapter cannot clear attachments", inputs_seen: 0, files_before: 0, files_after: 0 };
          const witness = activeAdapter.attachmentWitness?.(
            document,
            payload?.composer_keys_before ?? [],
            payload?.expected_name ?? "",
            payload?.expected_name_visible_before ?? false
          ) ?? null;
          sendResponse(replyTo(message, "attach.clear", withAttemptMetadata({
            ...result,
            adapter: activeAdapter.name,
            witness,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "prompt.stop": {
          const ok = activeAdapter.stopGeneration?.(document, window) ?? false;
          sendResponse(replyTo(message, "prompt.stop", withAttemptMetadata({ ok, adapter: activeAdapter.name, url: window.location.href }, attemptId)));
          return true;
        }
        case "chat.new": {
          const ok = activeAdapter.newChat?.(document) ?? false;
          sendResponse(replyTo(message, "chat.new", withAttemptMetadata({ ok, adapter: activeAdapter.name, url: window.location.href }, attemptId)));
          return true;
        }
        case "surface.overrides.get": {
          sendResponse(replyTo(message, "surface.overrides.get", withAttemptMetadata({
            ok: true,
            adapter: activeAdapter.name,
            overrides: getSurfaceOverrides(),
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "surface.overrides.set": {
          const requested = message.payload?.overrides ?? {};
          const next = requested && typeof requested === "object" ? requested : {};
          setSurfaceOverrides(next);
          chrome.storage.local.set({ [SURFACE_OVERRIDES_KEY]: next }).catch(() => void 0);
          sendResponse(replyTo(message, "surface.overrides.set", withAttemptMetadata({
            ok: true,
            adapter: activeAdapter.name,
            overrides: next,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "surface.probe": {
          const probe = activeAdapter.surfaceProbe?.(document, window) ?? null;
          sendResponse(replyTo(message, "surface.probe", withAttemptMetadata({
            ok: Boolean(probe),
            adapter: activeAdapter.name,
            probe,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        case "prompt.continue": {
          const ok = activeAdapter.continueGeneration?.(document, window) ?? false;
          const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
          sendResponse(replyTo(message, "prompt.continue", withAttemptMetadata({
            ok,
            adapter: activeAdapter.name,
            generation,
            url: window.location.href
          }, attemptId)));
          return true;
        }
        default:
          sendResponse(replyTo(message, "error.report", { error: `unsupported content-script request: ${message.type}`, adapter: activeAdapter.name }));
          return true;
      }
    });
  }
  function bootstrapContentRuntime() {
    if (globalScope.__glassttyContentBootstrap) {
      resolveAdapter("bootstrap-reused");
      log("bootstrap reused", globalScope.__glassttyContentBootstrap);
      return;
    }
    globalScope.__glassttyContentBootstrap = {
      version: CONTENT_BOOTSTRAP_VERSION,
      adapterName: adapter?.name,
      bootedAt: (/* @__PURE__ */ new Date()).toISOString()
    };
    installRuntimeLane();
    setInterval(() => pruneAttachTransfers(), 6e4);
    loadSurfaceOverrides();
    startAdapterWatcher();
    resolveAdapter("bootstrap");
    if (adapter) startTranscriptObserver();
  }
  bootstrapContentRuntime();
})();
