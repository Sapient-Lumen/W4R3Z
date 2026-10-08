export function makeEnvelope(type, payload, tab_id) {
    return {
        version: '0.1',
        request_id: crypto.randomUUID(),
        type,
        tab_id,
        timestamp: new Date().toISOString(),
        payload,
    };
}
export function replyTo(request, type, payload, tab_id) {
    return {
        version: '0.1',
        request_id: request.request_id,
        type,
        tab_id: tab_id ?? request.tab_id,
        timestamp: new Date().toISOString(),
        payload,
    };
}
