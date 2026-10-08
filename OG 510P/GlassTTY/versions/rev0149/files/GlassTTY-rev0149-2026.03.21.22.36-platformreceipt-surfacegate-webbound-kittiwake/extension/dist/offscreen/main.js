import { makeEnvelope, replyTo } from "../shared/protocol";
const EDITABLE_SELECTOR = [
    "textarea",
    "select",
    'input:not([type="hidden"]):not([type="button"]):not([type="submit"]):not([type="reset"]):not([type="image"])',
    '[contenteditable=""]',
    '[contenteditable="true"]',
    '[role="textbox"]',
    '[role="combobox"]',
    '[role="listbox"]',
    '[role="checkbox"]',
    '[role="radio"]',
    '[role="switch"]',
].join(", ");
const OUTPUT_SELECTORS = [
    '[data-testid*="assistant"]',
    '[data-testid*="message"]',
    '[data-message-author-role="assistant"]',
    '[role="log"]',
    "[aria-live]",
    "main",
    '[role="main"]',
    "article",
    ".prose",
].join(", ");
const SUBMIT_SELECTORS = [
    "button",
    'input[type="submit"]',
    'input[type="button"]',
    '[role="button"]',
].join(", ");
function currentPayload() {
    return {
        readyAt: new Date().toISOString(),
        href: globalThis.location?.href ?? "about:blank",
        title: globalThis.document?.title ?? "GlassTTY Offscreen",
        userAgent: globalThis.navigator?.userAgent ?? "",
        visibilityState: globalThis.document?.visibilityState ?? "hidden",
    };
}
function compactText(value, maxLength = 240) {
    const text = (value ?? "").replace(/\s+/g, " ").trim();
    if (text.length <= maxLength)
        return text;
    return `${text.slice(0, maxLength - 1)}…`;
}
function compactUnique(values, maxItems = 6, maxLength = 160) {
    const seen = new Set();
    const items = [];
    for (const value of values) {
        const text = compactText(value, maxLength);
        if (!text || seen.has(text))
            continue;
        seen.add(text);
        items.push(text);
        if (items.length >= maxItems)
            break;
    }
    return items;
}
function selectorHintForElement(element) {
    const tagName = element.tagName.toLowerCase();
    const id = element.getAttribute("id");
    const name = element.getAttribute("name");
    const type = element.getAttribute("type");
    const role = element.getAttribute("role");
    const parts = [tagName];
    if (id)
        parts.push(`#${id}`);
    if (name)
        parts.push(`[name=${JSON.stringify(name)}]`);
    if (type)
        parts.push(`[type=${JSON.stringify(type)}]`);
    if (role)
        parts.push(`[role=${JSON.stringify(role)}]`);
    return parts.join("");
}
function normalizeBaseUrl(value) {
    if (typeof value !== "string" || value.trim().length === 0)
        return undefined;
    try {
        return new URL(value).href;
    }
    catch {
        return undefined;
    }
}
function parseHtmlDocument(html) {
    const parser = new DOMParser();
    return parser.parseFromString(html, "text/html");
}
function resolveMaybe(urlValue, baseUrl) {
    const raw = (urlValue ?? "").trim();
    if (!raw)
        return undefined;
    if (!baseUrl) {
        try {
            return new URL(raw).href;
        }
        catch {
            return undefined;
        }
    }
    try {
        return new URL(raw, baseUrl).href;
    }
    catch {
        return undefined;
    }
}
function visibleHeuristic(element) {
    if (element.hasAttribute("hidden"))
        return false;
    if (element.getAttribute("aria-hidden") === "true")
        return false;
    const style = (element.getAttribute("style") ?? "").toLowerCase();
    if (style.includes("display:none") || style.includes("visibility:hidden"))
        return false;
    return true;
}
function nodeTextLength(element) {
    const input = element;
    const directText = compactText(element.textContent, 10_000);
    const value = "value" in input && typeof input.value === "string" ? input.value : "";
    return Math.max(value.length, directText.length);
}
function outerHtmlSample(element, maxLength = 1600) {
    if (!element)
        return null;
    const html = (element.outerHTML ?? "").replace(/\s+/g, " ").trim();
    if (!html)
        return null;
    if (html.length <= maxLength)
        return html;
    return `${html.slice(0, maxLength - 1)}…`;
}
function labelElementsForControl(element, doc) {
    const labels = [];
    const labeled = element;
    if (labeled.labels) {
        labels.push(...Array.from(labeled.labels));
    }
    for (const label of Array.from(doc.querySelectorAll("label"))) {
        if (!(label instanceof HTMLLabelElement))
            continue;
        if (label.control === element && !labels.includes(label)) {
            labels.push(label);
        }
    }
    return labels;
}
function ariaLabelledTexts(element, doc) {
    const labelledby = (element.getAttribute("aria-labelledby") ?? "").trim();
    if (!labelledby)
        return [];
    return compactUnique(labelledby
        .split(/\s+/)
        .map((id) => doc.getElementById(id)?.textContent ?? null), 6, 120);
}
function labelTextsForControl(element, doc) {
    return compactUnique(labelElementsForControl(element, doc).map((label) => label.textContent), 6, 120);
}
function textFallbackForElement(element, baseUrl) {
    if (element instanceof HTMLInputElement) {
        const type = (element.type ||
            element.getAttribute("type") ||
            "").toLowerCase();
        if (type === "submit" || type === "button" || type === "reset") {
            return compactUnique([
                element.value,
                element.getAttribute("value"),
                element.getAttribute("title"),
            ], 4, 120);
        }
        if (type === "checkbox" || type === "radio") {
            return compactUnique([element.value, element.getAttribute("title")], 4, 120);
        }
    }
    if (element instanceof HTMLButtonElement) {
        return compactUnique([
            element.textContent,
            element.getAttribute("aria-label"),
            element.getAttribute("title"),
        ], 4, 120);
    }
    if (element instanceof HTMLSelectElement) {
        return compactUnique(Array.from(element.selectedOptions).map((option) => option.textContent), 4, 120);
    }
    const formContext = baseUrl ? formContextForElement(element, baseUrl) : {};
    return compactUnique([
        element.getAttribute("placeholder"),
        element.getAttribute("title"),
        formContext.formName,
        element.textContent,
    ], 4, 120);
}
function accessibleNameTextsForControl(element, doc, baseUrl) {
    const labelledBy = ariaLabelledTexts(element, doc);
    if (labelledBy.length)
        return labelledBy;
    const ariaLabel = compactText(element.getAttribute("aria-label"), 120);
    if (ariaLabel)
        return [ariaLabel];
    const labels = labelTextsForControl(element, doc);
    if (labels.length)
        return labels;
    return textFallbackForElement(element, baseUrl);
}
function describedByTexts(element, doc) {
    const describedBy = (element.getAttribute("aria-describedby") ?? "").trim();
    if (!describedBy)
        return [];
    return compactUnique(describedBy
        .split(/\s+/)
        .map((id) => doc.getElementById(id)?.textContent ?? null), 6, 120);
}
function descriptionTextsForControl(element, doc) {
    const describedBy = describedByTexts(element, doc);
    if (describedBy.length)
        return describedBy;
    const ariaDescription = compactText(element.getAttribute("aria-description"), 120);
    const title = compactText(element.getAttribute("title"), 120);
    return compactUnique([ariaDescription || null, title || null], 6, 120);
}
function fieldsetLegendTextsForElement(element) {
    const legends = [];
    let currentFieldset = element.closest("fieldset");
    while (currentFieldset) {
        const directLegend = currentFieldset.querySelector(":scope > legend");
        const anyLegend = directLegend ?? currentFieldset.querySelector("legend");
        legends.push(anyLegend?.textContent ?? null);
        currentFieldset =
            currentFieldset.parentElement?.closest("fieldset") ?? null;
    }
    return compactUnique(legends, 4, 120);
}
function controlKindForElement(element) {
    const tag = element.tagName.toLowerCase();
    const role = (element.getAttribute("role") ?? "").toLowerCase();
    const type = (element.getAttribute("type") ?? "").toLowerCase();
    if (role === "searchbox" || type === "search")
        return "searchbox";
    if (role === "checkbox" || type === "checkbox")
        return "checkbox";
    if (role === "radio" || type === "radio")
        return "radio";
    if (role === "switch")
        return "switch";
    if (role === "listbox")
        return "listbox";
    if (role === "combobox" || tag === "select" || element.getAttribute("list"))
        return "combobox";
    if (role === "textbox" || tag === "textarea")
        return "textbox";
    if (tag === "input" && type)
        return `input:${type}`;
    if (element.getAttribute("contenteditable") === "true" ||
        element.getAttribute("contenteditable") === "")
        return "contenteditable";
    if (role)
        return `role:${role}`;
    return tag;
}
function owningFormForElement(element) {
    const owner = element;
    return owner.form ?? element.closest("form");
}
function formNameForElement(form, doc) {
    if (!form)
        return [];
    const labelledBy = ariaLabelledTexts(form, doc);
    if (labelledBy.length)
        return labelledBy;
    const ariaLabel = compactText(form.getAttribute("aria-label"), 120);
    if (ariaLabel)
        return [ariaLabel];
    const title = compactText(form.getAttribute("title"), 120);
    if (title)
        return [title];
    return [];
}
function optionSummaryForElement(element, doc) {
    if (element instanceof HTMLSelectElement) {
        const options = Array.from(element.options);
        return {
            optionCount: options.length,
            optionLabels: compactUnique(options.map((option) => option.textContent), 8, 120),
            selectedOptions: compactUnique(Array.from(element.selectedOptions).map((option) => option.textContent), 4, 120),
        };
    }
    if (element instanceof HTMLInputElement && element.getAttribute("list")) {
        const listId = element.getAttribute("list");
        const datalist = listId ? doc.getElementById(listId) : null;
        if (datalist instanceof HTMLDataListElement) {
            const options = Array.from(datalist.options);
            return {
                optionCount: options.length,
                optionLabels: compactUnique(options.map((option) => option.label || option.value || option.textContent), 8, 120),
            };
        }
    }
    const role = (element.getAttribute("role") ?? "").toLowerCase();
    if (role === "listbox" || role === "combobox") {
        const options = Array.from(element.querySelectorAll('[role="option"]'));
        if (options.length) {
            return {
                optionCount: options.length,
                optionLabels: compactUnique(options.map((option) => option.textContent), 8, 120),
                selectedOptions: compactUnique(options
                    .filter((option) => option.getAttribute("aria-selected") === "true")
                    .map((option) => option.textContent), 4, 120),
            };
        }
    }
    return {};
}
function constraintHintsForElement(element) {
    const hints = compactUnique([
        element.hasAttribute("pattern")
            ? `pattern:${element.getAttribute("pattern")}`
            : null,
        element.hasAttribute("min") ? `min:${element.getAttribute("min")}` : null,
        element.hasAttribute("max") ? `max:${element.getAttribute("max")}` : null,
        element.hasAttribute("step")
            ? `step:${element.getAttribute("step")}`
            : null,
        element.hasAttribute("minlength")
            ? `minlength:${element.getAttribute("minlength")}`
            : null,
        element.hasAttribute("maxlength")
            ? `maxlength:${element.getAttribute("maxlength")}`
            : null,
        element.hasAttribute("accept")
            ? `accept:${element.getAttribute("accept")}`
            : null,
    ], 8, 120);
    return hints;
}
function choiceGroupForElement(element, doc, baseUrl) {
    const roleGroup = element.closest('[role="radiogroup"], [role="group"], [role="listbox"], [role="combobox"]');
    const roleGroupNames = roleGroup
        ? accessibleNameTextsForControl(roleGroup, doc, baseUrl)
        : [];
    const fieldsetLegends = fieldsetLegendTextsForElement(element);
    const formContext = formContextForElement(element, baseUrl);
    const choiceGroup = compactUnique([
        element.getAttribute("name"),
        roleGroupNames[0] ?? null,
        fieldsetLegends[0] ?? null,
        formContext.formName ?? null,
    ], 4, 120);
    return choiceGroup[0] ?? undefined;
}
function controlStateForElement(element, doc, baseUrl) {
    const disabled = element.disabled === true ||
        element.hasAttribute("disabled") ||
        element.closest("fieldset[disabled]") !== null ||
        element.getAttribute("aria-disabled") === "true";
    const readonly = element.readOnly === true ||
        element.hasAttribute("readonly") ||
        element.getAttribute("aria-readonly") === "true";
    const multiple = (element instanceof HTMLSelectElement && element.multiple) ||
        (element instanceof HTMLInputElement && element.multiple) ||
        element.getAttribute("aria-multiselectable") === "true";
    const autocomplete = compactText(element.getAttribute("autocomplete") ||
        owningFormForElement(element)?.getAttribute("autocomplete"), 120);
    const inputMode = compactText(element.getAttribute("inputmode"), 60);
    let checkedState;
    if (element instanceof HTMLInputElement &&
        (element.type === "checkbox" || element.type === "radio")) {
        checkedState = element.indeterminate
            ? "mixed"
            : element.checked
                ? "checked"
                : "unchecked";
    }
    else {
        const ariaChecked = (element.getAttribute("aria-checked") ?? "").toLowerCase();
        if (ariaChecked === "true")
            checkedState = "checked";
        else if (ariaChecked === "false")
            checkedState = "unchecked";
        else if (ariaChecked === "mixed")
            checkedState = "mixed";
    }
    let selectedCount;
    if (element instanceof HTMLSelectElement) {
        selectedCount = element.selectedOptions.length;
    }
    else {
        const role = (element.getAttribute("role") ?? "").toLowerCase();
        if (role === "listbox" || role === "combobox") {
            selectedCount = element.querySelectorAll('[role="option"][aria-selected="true"]').length;
        }
    }
    const choiceGroup = choiceGroupForElement(element, doc, baseUrl);
    const constraintHints = constraintHintsForElement(element);
    return {
        ...(typeof checkedState === "string" ? { checkedState } : {}),
        ...(disabled ? { disabled: true } : {}),
        ...(readonly ? { readonly: true } : {}),
        ...(multiple ? { multiple: true } : {}),
        ...(typeof selectedCount === "number" ? { selectedCount } : {}),
        ...(autocomplete ? { autocomplete } : {}),
        ...(inputMode ? { inputMode } : {}),
        ...(constraintHints.length ? { constraintHints } : {}),
        ...(choiceGroup ? { choiceGroup } : {}),
    };
}
function validationStateForElement(element) {
    const required = element.hasAttribute("required") ||
        element.getAttribute("aria-required") === "true";
    const invalidAttr = (element.getAttribute("aria-invalid") ?? "").toLowerCase();
    const flags = [];
    const control = element;
    if (control.validity) {
        for (const key of [
            "valueMissing",
            "typeMismatch",
            "patternMismatch",
            "tooLong",
            "tooShort",
            "rangeUnderflow",
            "rangeOverflow",
            "stepMismatch",
            "badInput",
            "customError",
        ]) {
            if (control.validity[key])
                flags.push(key);
        }
    }
    if (invalidAttr === "grammar" || invalidAttr === "spelling") {
        flags.push(`aria-invalid:${invalidAttr}`);
    }
    const invalid = invalidAttr === "true" ||
        invalidAttr === "grammar" ||
        invalidAttr === "spelling" ||
        (typeof control.checkValidity === "function"
            ? !control.checkValidity()
            : flags.length > 0);
    return {
        ...(required ? { required: true } : {}),
        ...(invalid ? { invalid: true } : {}),
        ...(flags.length ? { constraintFlags: compactUnique(flags, 10, 80) } : {}),
    };
}
function formContextForElement(element, baseUrl) {
    const form = owningFormForElement(element);
    if (!form)
        return {};
    const formNames = formNameForElement(form, form.ownerDocument ?? document);
    return {
        ...(formNames.length ? { formName: formNames[0] } : {}),
        formAction: resolveMaybe(form.getAttribute("action"), baseUrl) ??
            form.getAttribute("action") ??
            undefined,
        formMethod: (form.getAttribute("method") ?? "get").toLowerCase(),
    };
}
function dialogContextForElement(element, doc, baseUrl) {
    const dialog = element.closest('dialog, [role="dialog"], [role="alertdialog"]');
    if (!dialog || !(doc.body ?? doc.documentElement)?.contains(dialog))
        return {};
    const dialogNames = accessibleNameTextsForControl(dialog, doc, baseUrl);
    const role = compactText(dialog.getAttribute("role"), 40) ||
        (dialog.tagName.toLowerCase() === "dialog" ? "dialog" : undefined);
    const ariaModal = compactText(dialog.getAttribute("aria-modal"), 20);
    const modal = ariaModal === "true" ||
        (dialog instanceof HTMLDialogElement && typeof dialog.matches === "function" && dialog.matches(":modal"));
    const open = dialog instanceof HTMLDialogElement
        ? dialog.open
        : dialog.hasAttribute("open") || ariaModal === "true";
    return {
        ...(dialogNames.length ? { dialogName: dialogNames[0] } : {}),
        ...(role ? { dialogRole: role } : {}),
        ...(modal ? { dialogModal: true } : {}),
        ...(open ? { dialogOpen: true } : {}),
    };
}
function collectDialogSamples(doc, baseUrl) {
    return Array.from(doc.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]'))
        .slice(0, 6)
        .map((dialog) => {
        const names = accessibleNameTextsForControl(dialog, doc, baseUrl);
        const role = compactText(dialog.getAttribute("role"), 40) ||
            (dialog.tagName.toLowerCase() === "dialog" ? "dialog" : "dialog");
        const ariaModal = compactText(dialog.getAttribute("aria-modal"), 20);
        const modal = ariaModal === "true" ||
            (dialog instanceof HTMLDialogElement && typeof dialog.matches === "function" && dialog.matches(":modal"));
        const open = dialog instanceof HTMLDialogElement
            ? dialog.open
            : dialog.hasAttribute("open") || ariaModal === "true";
        return {
            selectorHint: selectorHintForElement(dialog),
            role,
            ...(names.length ? { name: names[0] } : {}),
            ...(modal ? { modal: true } : {}),
            ...(open ? { open: true } : {}),
        };
    });
}
function collectIframeSamples(doc, baseUrl) {
    return Array.from(doc.querySelectorAll("iframe"))
        .slice(0, 8)
        .map((frame) => ({
        selectorHint: selectorHintForElement(frame),
        src: frame.getAttribute("src") ?? undefined,
        resolvedSrc: resolveMaybe(frame.getAttribute("src"), baseUrl),
        name: compactText(frame.getAttribute("name"), 120) || undefined,
        title: compactText(frame.getAttribute("title"), 160) || undefined,
    }));
}
function submitContextForElement(element, baseUrl) {
    let submitAction;
    let submitMethod;
    let submitTarget;
    if (element instanceof HTMLButtonElement) {
        submitAction =
            resolveMaybe(element.formAction || element.getAttribute("formaction"), baseUrl) ??
                element.getAttribute("formaction") ??
                undefined;
        submitMethod =
            compactText(element.formMethod || element.getAttribute("formmethod"), 40).toLowerCase() || undefined;
        submitTarget =
            compactText(element.formTarget || element.getAttribute("formtarget"), 80) || undefined;
    }
    else if (element instanceof HTMLInputElement) {
        submitAction =
            resolveMaybe(element.formAction || element.getAttribute("formaction"), baseUrl) ??
                element.getAttribute("formaction") ??
                undefined;
        submitMethod =
            compactText(element.formMethod || element.getAttribute("formmethod"), 40).toLowerCase() || undefined;
        submitTarget =
            compactText(element.formTarget || element.getAttribute("formtarget"), 80) || undefined;
    }
    if (!submitAction || !submitMethod) {
        const formContext = formContextForElement(element, baseUrl);
        submitAction = submitAction ?? formContext.formAction;
        submitMethod = submitMethod ?? formContext.formMethod;
    }
    return {
        ...(submitAction ? { submitAction } : {}),
        ...(submitMethod ? { submitMethod } : {}),
        ...(submitTarget ? { submitTarget } : {}),
    };
}
function candidateInfo(element, score, doc, baseUrl) {
    const labels = labelTextsForControl(element, doc);
    const accessibleNames = accessibleNameTextsForControl(element, doc, baseUrl);
    const descriptions = descriptionTextsForControl(element, doc);
    const fieldsetLegends = fieldsetLegendTextsForElement(element);
    const dialogContext = dialogContextForElement(element, doc, baseUrl);
    const formContext = formContextForElement(element, baseUrl);
    const optionSummary = optionSummaryForElement(element, doc);
    const controlState = controlStateForElement(element, doc, baseUrl);
    const validation = validationStateForElement(element);
    return {
        selector_hint: selectorHintForElement(element),
        score,
        text_length: nodeTextLength(element),
        visible: visibleHeuristic(element),
        ...(labels.length ? { label_text: labels[0], labels } : {}),
        ...(accessibleNames.length
            ? {
                accessible_name: accessibleNames[0],
                accessible_names: accessibleNames,
            }
            : {}),
        ...(descriptions.length
            ? { description_text: descriptions[0], descriptions }
            : {}),
        ...(fieldsetLegends.length
            ? {
                fieldset_legend: fieldsetLegends[0],
                fieldset_legends: fieldsetLegends,
            }
            : {}),
        ...(dialogContext.dialogName ? { dialog_name: dialogContext.dialogName } : {}),
        ...(dialogContext.dialogRole ? { dialog_role: dialogContext.dialogRole } : {}),
        ...(dialogContext.dialogModal ? { dialog_modal: true } : {}),
        ...(dialogContext.dialogOpen ? { dialog_open: true } : {}),
        control_kind: controlKindForElement(element),
        ...(formContext.formName ? { form_name: formContext.formName } : {}),
        ...(formContext.formAction ? { form_action: formContext.formAction } : {}),
        ...(formContext.formMethod ? { form_method: formContext.formMethod } : {}),
        ...(typeof optionSummary.optionCount === "number"
            ? { option_count: optionSummary.optionCount }
            : {}),
        ...(optionSummary.optionLabels?.length
            ? { option_labels: optionSummary.optionLabels }
            : {}),
        ...(optionSummary.selectedOptions?.length
            ? { selected_options: optionSummary.selectedOptions }
            : {}),
        ...(typeof controlState.checkedState === "string"
            ? { checked_state: controlState.checkedState }
            : {}),
        ...(controlState.disabled ? { disabled: true } : {}),
        ...(controlState.readonly ? { readonly: true } : {}),
        ...(controlState.multiple ? { multiple: true } : {}),
        ...(typeof controlState.selectedCount === "number"
            ? { selected_count: controlState.selectedCount }
            : {}),
        ...(controlState.autocomplete
            ? { autocomplete: controlState.autocomplete }
            : {}),
        ...(controlState.inputMode ? { input_mode: controlState.inputMode } : {}),
        ...(controlState.constraintHints?.length
            ? { constraint_hints: controlState.constraintHints }
            : {}),
        ...(controlState.choiceGroup
            ? { choice_group: controlState.choiceGroup }
            : {}),
        ...validation,
    };
}
function textishIdentity(element, doc, baseUrl) {
    const labels = labelTextsForControl(element, doc).join(" ").toLowerCase();
    const accessibleNames = accessibleNameTextsForControl(element, doc, baseUrl)
        .join(" ")
        .toLowerCase();
    const descriptions = descriptionTextsForControl(element, doc)
        .join(" ")
        .toLowerCase();
    const legends = fieldsetLegendTextsForElement(element)
        .join(" ")
        .toLowerCase();
    const placeholder = (element.getAttribute("placeholder") ?? "").toLowerCase();
    const aria = (element.getAttribute("aria-label") ?? "").toLowerCase();
    const name = (element.getAttribute("name") ?? "").toLowerCase();
    const type = (element.getAttribute("type") ?? "").toLowerCase();
    const optionLabels = (optionSummaryForElement(element, doc).optionLabels ?? [])
        .join(" ")
        .toLowerCase();
    return `${labels} ${accessibleNames} ${descriptions} ${legends} ${placeholder} ${aria} ${name} ${type} ${optionLabels}`;
}
function promptScore(element, doc) {
    const tag = element.tagName.toLowerCase();
    const role = (element.getAttribute("role") ?? "").toLowerCase();
    const type = (element.getAttribute("type") ?? "").toLowerCase();
    const identity = textishIdentity(element, doc);
    let score = 1;
    if (tag === "textarea")
        score += 4;
    if (tag === "select")
        score += 2;
    if (tag === "input")
        score += 3;
    if (type === "checkbox" || type === "radio")
        score -= 1;
    if (element.getAttribute("contenteditable") === "true" ||
        element.getAttribute("contenteditable") === "")
        score += 4;
    if (role === "textbox")
        score += 3;
    if (role === "combobox" || role === "listbox")
        score += 2;
    if (/prompt|message|chat|ask|write|send|question|reply|input|email|password|code|search|topic|subject/.test(identity))
        score += 4;
    if (element.closest("form"))
        score += 1;
    if (!visibleHeuristic(element))
        score -= 3;
    score += Math.min(3, Math.floor(nodeTextLength(element) / 80));
    return score;
}
function outputScore(element) {
    const selectorHint = selectorHintForElement(element).toLowerCase();
    const dataRole = (element.getAttribute("data-message-author-role") ?? "").toLowerCase();
    const role = (element.getAttribute("role") ?? "").toLowerCase();
    let score = 1;
    if (dataRole === "assistant")
        score += 5;
    if (role === "main" || role === "log")
        score += 3;
    if (/assistant|message|output|response|article|main|prose/.test(selectorHint))
        score += 3;
    if (element.tagName.toLowerCase() === "article" ||
        element.tagName.toLowerCase() === "main")
        score += 2;
    if (element.hasAttribute("aria-live"))
        score += 1;
    if (!visibleHeuristic(element))
        score -= 3;
    score += Math.min(6, Math.floor(nodeTextLength(element) / 160));
    return score;
}
function submitScore(element, doc) {
    const tag = element.tagName.toLowerCase();
    const role = (element.getAttribute("role") ?? "").toLowerCase();
    const type = (element.getAttribute("type") ?? "").toLowerCase();
    const text = compactText(element.value ||
        element.textContent ||
        element.getAttribute("aria-label"), 240).toLowerCase();
    const identity = `${text} ${textishIdentity(element, doc)} ${role}`;
    let score = 0;
    if (tag === "button")
        score += 3;
    if (tag === "input" && (type === "submit" || type === "button"))
        score += 4;
    if (role === "button")
        score += 2;
    if (/send|submit|continue|save|reply|ask|search|go|next|create|login|sign in|sign up/.test(identity))
        score += 4;
    if (element.closest("form"))
        score += 2;
    if (!visibleHeuristic(element))
        score -= 3;
    score += Math.min(2, Math.floor(nodeTextLength(element) / 32));
    return score;
}
function dedupeCandidates(candidates, maxCandidates) {
    const seen = new Set();
    const unique = [];
    for (const item of candidates.sort((a, b) => b.info.score - a.info.score || b.info.text_length - a.info.text_length)) {
        const key = item.info.selector_hint;
        if (seen.has(key))
            continue;
        seen.add(key);
        unique.push(item);
        if (unique.length >= maxCandidates)
            break;
    }
    return unique;
}
function collectCandidates(doc, selectors, scorer, maxCandidates, baseUrl) {
    return dedupeCandidates(Array.from(doc.querySelectorAll(selectors)).map((element) => ({
        element,
        info: candidateInfo(element, scorer(element, doc), doc, baseUrl),
    })), maxCandidates);
}
function collectSubmitCandidates(doc, maxCandidates, baseUrl) {
    return dedupeCandidates(Array.from(doc.querySelectorAll(SUBMIT_SELECTORS))
        .map((element) => {
        const info = candidateInfo(element, submitScore(element, doc), doc, baseUrl);
        const submitContext = submitContextForElement(element, baseUrl);
        const textSample = compactText(element.value ||
            element.textContent ||
            element.getAttribute("aria-label"), 120);
        return {
            element,
            info: {
                ...info,
                ...submitContext,
                role: element.getAttribute("role") ?? undefined,
                ...(textSample ? { text_sample: textSample } : {}),
            },
        };
    })
        .filter((item) => item.info.score > 0), maxCandidates);
}
function semanticOutline(summary, inputs, submits) {
    const linkHosts = compactUnique(summary.linkSamples.map((sample) => {
        const candidate = sample.resolvedHref ?? sample.href;
        if (!candidate)
            return null;
        try {
            return new URL(candidate).host;
        }
        catch {
            return candidate;
        }
    }), 8, 120);
    return {
        heading_outline: compactUnique(summary.headings.map((heading) => `${heading.level}:${heading.text}`), 8, 160),
        prompt_labels: compactUnique(inputs.flatMap((item) => item.info.labels ??
            (item.info.label_text ? [item.info.label_text] : [])), 8, 120),
        accessible_names: compactUnique(inputs.flatMap((item) => item.info.accessible_names ??
            (item.info.accessible_name ? [item.info.accessible_name] : [])), 8, 120),
        prompt_descriptions: compactUnique(inputs.flatMap((item) => item.info.descriptions ??
            (item.info.description_text ? [item.info.description_text] : [])), 8, 120),
        submit_labels: compactUnique(submits.flatMap((item) => [
            item.info.accessible_name,
            item.info.label_text,
            item.info.text_sample,
        ]), 8, 120),
        form_names: compactUnique(inputs.flatMap((item) => [item.info.form_name]), 8, 120),
        form_actions: compactUnique(submits.flatMap((item) => [
            item.info.submit_action,
            item.info.form_action,
        ]), 8, 160),
        fieldset_legends: compactUnique(inputs.flatMap((item) => item.info.fieldset_legends ??
            (item.info.fieldset_legend ? [item.info.fieldset_legend] : [])), 8, 120),
        dialog_names: compactUnique([
            ...inputs.map((item) => item.info.dialog_name ?? null),
            ...summary.dialogSamples.map((sample) => sample.name ?? null),
        ], 8, 120),
        iframe_names: compactUnique(summary.iframeSamples.map((sample) => sample.name ?? null), 8, 120),
        iframe_titles: compactUnique(summary.iframeSamples.map((sample) => sample.title ?? null), 8, 160),
        control_kinds: compactUnique(inputs.map((item) => item.info.control_kind ?? null), 8, 80),
        option_labels: compactUnique(inputs.flatMap((item) => item.info.option_labels ?? []), 8, 120),
        choice_groups: compactUnique(inputs.map((item) => item.info.choice_group ?? null), 8, 120),
        autocomplete_tokens: compactUnique(inputs.map((item) => item.info.autocomplete ?? null), 8, 120),
        state_flags: compactUnique(inputs.flatMap((item) => [
            item.info.required ? "required" : null,
            item.info.invalid ? "invalid" : null,
            item.info.disabled ? "disabled" : null,
            item.info.readonly ? "readonly" : null,
            item.info.multiple ? "multiple" : null,
            item.info.checked_state ? `checked:${item.info.checked_state}` : null,
        ]), 12, 80),
        constraint_hints: compactUnique(inputs.flatMap((item) => item.info.constraint_hints ?? []), 12, 120),
        link_hosts: linkHosts,
    };
}
function summarizeHtml(html, selectors, maxCandidates, baseUrl) {
    const doc = parseHtmlDocument(html);
    const selectorMatches = selectors.map((selector) => {
        try {
            return { selector, count: doc.querySelectorAll(selector).length };
        }
        catch (error) {
            return {
                selector,
                count: 0,
                error: error instanceof Error ? error.message : String(error),
            };
        }
    });
    const editableElements = Array.from(doc.querySelectorAll(EDITABLE_SELECTOR));
    const editableCandidates = editableElements
        .slice(0, maxCandidates)
        .map((element) => {
        const input = element;
        const directText = compactText(element.textContent, 200);
        const value = "value" in input && typeof input.value === "string" ? input.value : "";
        const labels = labelTextsForControl(element, doc);
        const accessibleNames = accessibleNameTextsForControl(element, doc, baseUrl);
        const descriptions = descriptionTextsForControl(element, doc);
        const fieldsetLegends = fieldsetLegendTextsForElement(element);
        const dialogContext = dialogContextForElement(element, doc, baseUrl);
        const formContext = formContextForElement(element, baseUrl);
        const optionSummary = optionSummaryForElement(element, doc);
        const controlState = controlStateForElement(element, doc, baseUrl);
        const validation = validationStateForElement(element);
        return {
            tagName: element.tagName.toLowerCase(),
            type: element.getAttribute("type") ?? undefined,
            id: element.getAttribute("id") ?? undefined,
            name: element.getAttribute("name") ?? undefined,
            placeholder: element.getAttribute("placeholder") ?? undefined,
            ariaLabel: element.getAttribute("aria-label") ?? undefined,
            selectorHint: selectorHintForElement(element),
            valueLength: value.length,
            textLength: directText.length,
            ...(labels.length ? { labelText: labels[0], labels } : {}),
            ...(accessibleNames.length
                ? { accessibleName: accessibleNames[0], accessibleNames }
                : {}),
            ...(descriptions.length
                ? { descriptionText: descriptions[0], descriptions }
                : {}),
            ...(fieldsetLegends.length
                ? { fieldsetLegend: fieldsetLegends[0], fieldsetLegends }
                : {}),
            ...(dialogContext.dialogName ? { dialogName: dialogContext.dialogName } : {}),
            ...(dialogContext.dialogRole ? { dialogRole: dialogContext.dialogRole } : {}),
            ...(dialogContext.dialogModal ? { dialogModal: true } : {}),
            ...(dialogContext.dialogOpen ? { dialogOpen: true } : {}),
            controlKind: controlKindForElement(element),
            ...(formContext.formName ? { formName: formContext.formName } : {}),
            ...(formContext.formAction
                ? { formAction: formContext.formAction }
                : {}),
            ...(formContext.formMethod
                ? { formMethod: formContext.formMethod }
                : {}),
            ...(typeof optionSummary.optionCount === "number"
                ? { optionCount: optionSummary.optionCount }
                : {}),
            ...(optionSummary.optionLabels?.length
                ? { optionLabels: optionSummary.optionLabels }
                : {}),
            ...(optionSummary.selectedOptions?.length
                ? { selectedOptions: optionSummary.selectedOptions }
                : {}),
            ...(typeof controlState.checkedState === "string"
                ? { checkedState: controlState.checkedState }
                : {}),
            ...(controlState.disabled ? { disabled: true } : {}),
            ...(controlState.readonly ? { readonly: true } : {}),
            ...(controlState.multiple ? { multiple: true } : {}),
            ...(typeof controlState.selectedCount === "number"
                ? { selectedCount: controlState.selectedCount }
                : {}),
            ...(controlState.autocomplete
                ? { autocomplete: controlState.autocomplete }
                : {}),
            ...(controlState.inputMode
                ? { inputMode: controlState.inputMode }
                : {}),
            ...(controlState.constraintHints?.length
                ? { constraintHints: controlState.constraintHints }
                : {}),
            ...(controlState.choiceGroup
                ? { choiceGroup: controlState.choiceGroup }
                : {}),
            ...validation,
        };
    });
    const headings = Array.from(doc.querySelectorAll("h1, h2, h3"))
        .slice(0, 8)
        .map((heading) => ({
        level: heading.tagName.toLowerCase(),
        text: compactText(heading.textContent, 160),
    }));
    const linkSamples = Array.from(doc.querySelectorAll("a[href]"))
        .slice(0, 8)
        .map((link) => ({
        text: compactText(link.textContent, 120),
        href: link.getAttribute("href") ?? "",
        resolvedHref: resolveMaybe(link.getAttribute("href"), baseUrl),
    }));
    const formSamples = Array.from(doc.querySelectorAll("form"))
        .slice(0, 6)
        .map((form) => ({
        method: (form.getAttribute("method") ?? "get").toLowerCase(),
        action: form.getAttribute("action") ?? undefined,
        resolvedAction: resolveMaybe(form.getAttribute("action"), baseUrl),
        inputCount: form.querySelectorAll("input").length,
        textareaCount: form.querySelectorAll("textarea").length,
        buttonCount: form.querySelectorAll('button, input[type="button"], input[type="submit"]').length,
    }));
    const dialogSamples = collectDialogSamples(doc, baseUrl);
    const iframeSamples = collectIframeSamples(doc, baseUrl);
    const submitCandidates = collectSubmitCandidates(doc, maxCandidates, baseUrl).map((item) => item.info);
    const promptCandidates = collectCandidates(doc, EDITABLE_SELECTOR, promptScore, maxCandidates, baseUrl);
    const bodyText = compactText(doc.body?.textContent, 400);
    return {
        parsedAt: new Date().toISOString(),
        title: compactText(doc.title, 200),
        ...(baseUrl ? { baseUrl } : {}),
        textLength: compactText(doc.body?.textContent, 20_000).length,
        textSample: bodyText,
        linkCount: doc.querySelectorAll("a[href]").length,
        buttonCount: doc.querySelectorAll('button, input[type="button"], input[type="submit"]').length,
        formCount: doc.querySelectorAll("form").length,
        dialogCount: doc.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]').length,
        iframeCount: doc.querySelectorAll("iframe").length,
        textareaCount: doc.querySelectorAll("textarea").length,
        inputCount: doc.querySelectorAll("input").length,
        editableCount: editableElements.length,
        selectorMatches,
        headings,
        editableCandidates,
        submitCandidates,
        semanticOutline: semanticOutline({ headings, linkSamples, formSamples, dialogSamples, iframeSamples }, promptCandidates, submitCandidates.map((info) => ({
            element: doc.body ?? doc.documentElement,
            info,
        }))),
        linkSamples,
        formSamples,
        dialogSamples,
        iframeSamples,
    };
}
function captureFixture(html, selectors, maxCandidates, baseUrl) {
    const doc = parseHtmlDocument(html);
    const summary = summarizeHtml(html, selectors, maxCandidates, baseUrl);
    const inputs = collectCandidates(doc, EDITABLE_SELECTOR, promptScore, maxCandidates, baseUrl);
    const outputs = collectCandidates(doc, OUTPUT_SELECTORS, (element) => outputScore(element), maxCandidates, baseUrl);
    const submits = collectSubmitCandidates(doc, maxCandidates, baseUrl);
    const bestInput = inputs[0]?.element;
    const bestOutput = outputs[0]?.element;
    const bestSubmit = submits[0]?.element;
    const bestInputText = bestInput
        ? compactText(bestInput.value ||
            bestInput.textContent, 20_000)
        : "";
    const bestOutputText = bestOutput
        ? compactText(bestOutput.textContent, 20_000)
        : "";
    return {
        summary,
        fixture: {
            adapter: "offscreen-html",
            url: baseUrl ?? "about:blank",
            title: summary.title || undefined,
            prompt: bestInputText || null,
            latest_output: bestOutputText || null,
            selection: null,
            candidates: {
                inputs: inputs.map((item) => item.info),
                outputs: outputs.map((item) => item.info),
            },
            html_samples: {
                prompt: outerHtmlSample(bestInput),
                latest_output: outerHtmlSample(bestOutput),
                submit: outerHtmlSample(bestSubmit),
            },
            metadata: {
                mode: "offscreen-fixture",
                base_url: baseUrl ?? null,
                link_count: summary.linkCount,
                form_count: summary.formCount,
                dialog_count: summary.dialogCount,
                iframe_count: summary.iframeCount,
                editable_count: summary.editableCount,
                heading_count: summary.headings.length,
                selector_matches: summary.selectorMatches,
                top_input_label: inputs[0]?.info.label_text ?? null,
                top_input_accessible_name: inputs[0]?.info.accessible_name ?? inputs[0]?.info.label_text ?? null,
                top_input_description: inputs[0]?.info.description_text ?? null,
                top_fieldset_legend: inputs[0]?.info.fieldset_legend ?? null,
                top_dialog_name: inputs[0]?.info.dialog_name ?? null,
                top_form_name: inputs[0]?.info.form_name ?? null,
                top_option_count: inputs[0]?.info.option_count ?? null,
                top_selected_option: inputs[0]?.info.selected_options?.[0] ?? null,
                top_checked_state: inputs[0]?.info.checked_state ?? null,
                top_disabled: inputs[0]?.info.disabled ?? false,
                top_readonly: inputs[0]?.info.readonly ?? false,
                top_multiple: inputs[0]?.info.multiple ?? false,
                top_selected_count: inputs[0]?.info.selected_count ?? null,
                top_autocomplete: inputs[0]?.info.autocomplete ?? null,
                top_input_mode: inputs[0]?.info.input_mode ?? null,
                top_choice_group: inputs[0]?.info.choice_group ?? null,
                top_constraint_hints: inputs[0]?.info.constraint_hints ?? [],
                top_constraint_flags: inputs[0]?.info.constraint_flags ?? [],
                top_submit_label: submits[0]?.info.accessible_name ??
                    submits[0]?.info.label_text ??
                    submits[0]?.info.text_sample ??
                    null,
                top_submit_action: submits[0]?.info.submit_action ??
                    submits[0]?.info.form_action ??
                    null,
                submit_candidates: submits.map((item) => item.info),
                semantic_outline: summary.semanticOutline,
                dialog_samples: summary.dialogSamples,
                iframe_samples: summary.iframeSamples,
                form_actions: summary.semanticOutline.form_actions,
            },
        },
    };
}
async function announceReady() {
    try {
        await chrome.runtime.sendMessage(makeEnvelope("offscreen.document_ready", currentPayload()));
    }
    catch (error) {
        console.error("[GlassTTY offscreen] ready announce failed", error);
    }
}
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === "offscreen.document_ping") {
        sendResponse(replyTo(message, "offscreen.document_pong", currentPayload()));
        return true;
    }
    if (message.type === "offscreen.document_parse_html") {
        const payload = message.payload ?? {};
        const html = typeof payload.html === "string" ? payload.html : "";
        const selectors = Array.isArray(payload.selectors)
            ? payload.selectors.filter((value) => typeof value === "string" && value.trim().length > 0)
            : [];
        const requestedMax = Number(payload.max_candidates ?? 8);
        const maxCandidates = Number.isFinite(requestedMax)
            ? Math.max(1, Math.min(24, Math.trunc(requestedMax)))
            : 8;
        const baseUrl = normalizeBaseUrl(payload.base_url);
        try {
            const summary = summarizeHtml(html, selectors, maxCandidates, baseUrl);
            sendResponse(replyTo(message, "offscreen.document_parse_html_result", {
                ok: true,
                summary,
            }));
        }
        catch (error) {
            sendResponse(replyTo(message, "offscreen.document_parse_html_result", {
                ok: false,
                error: error instanceof Error ? error.message : String(error),
            }));
        }
        return true;
    }
    if (message.type === "offscreen.document_capture_fixture") {
        const payload = message.payload ?? {};
        const html = typeof payload.html === "string" ? payload.html : "";
        const selectors = Array.isArray(payload.selectors)
            ? payload.selectors.filter((value) => typeof value === "string" && value.trim().length > 0)
            : [];
        const requestedMax = Number(payload.max_candidates ?? 8);
        const maxCandidates = Number.isFinite(requestedMax)
            ? Math.max(1, Math.min(24, Math.trunc(requestedMax)))
            : 8;
        const baseUrl = normalizeBaseUrl(payload.base_url);
        try {
            const capture = captureFixture(html, selectors, maxCandidates, baseUrl);
            sendResponse(replyTo(message, "offscreen.document_capture_fixture_result", {
                ok: true,
                ...capture,
            }));
        }
        catch (error) {
            sendResponse(replyTo(message, "offscreen.document_capture_fixture_result", {
                ok: false,
                error: error instanceof Error ? error.message : String(error),
            }));
        }
        return true;
    }
    return false;
});
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        void announceReady();
    }, { once: true });
}
else {
    void announceReady();
}
