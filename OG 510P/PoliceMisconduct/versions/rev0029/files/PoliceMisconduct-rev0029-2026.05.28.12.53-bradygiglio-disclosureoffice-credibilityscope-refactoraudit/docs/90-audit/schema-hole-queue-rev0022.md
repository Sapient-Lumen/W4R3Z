# Schema hole queue

The cube now has hundreds of JSON surfaces. Many are valid JSON and semantically useful, but not all row-array surfaces carry explicit machine schema pointers. Rev0022 queues likely schema holes for future tightening while keeping universal schema enforcement off.

The queue is deliberately non-destructive. It identifies work; it does not claim all schemas are complete.

