# Process capture-pipe and worker-result ownership (rev0978)

Rev0978 closes two lifecycle inversions in existing bounded owners. It does not
add a process registry, a worker framework, or a new authority layer.

## Measured subprocess failure

The shared argv/shell owner treated direct-child exit as command completion. A
command could exit with status zero after starting a background descendant that
inherited stdout or stderr. The descendant still owned the write end of the
capture pipe, so the reader never observed EOF. Micromax returned after its
short drain grace but left the descendant plus daemon capture threads alive.

The baseline transcript used the real `run_argv_bounded()` owner. The direct
child returned zero in about one second while its 30-second descendant and two
capture threads remained alive. A second case moved the descendant into a new
POSIX session, defeating ancestry/process-group cleanup while retaining the
same pipes.

Linux `pipe(7)` states the relevant ownership rule: a reader sees EOF only after
all file descriptors referring to the write end are closed. Direct-child status
is therefore insufficient evidence. Rev0978 records each capture pipe's
`(st_dev, st_ino)` identity and, only when a capture thread still lacks EOF
after the direct child has stopped, streams `/proc/*/fd` for processes retaining
that exact pipe object. Only those proven holder process identities receive
TERM and then forceful teardown. Where Python and Linux expose pidfds, Micromax
opens a stable pidfd, revalidates pipe ownership, and signals through that fd so
a recycled numeric PID cannot receive the signal. The older-Linux fallback
rechecks both `/proc/<pid>/stat` start time and exact pipe ownership immediately
before numeric signaling. This avoids killing a same-group sibling that
redirected all standard descriptors and owns no capture resource. The confirmed
child process group remains the fallback only where exact Linux discovery is
unavailable; an empty exact scan never broadens teardown authority.

The same mechanism covers a blocked stdin writer: if a descendant retains the
read end after its parent exits, Micromax releases that exact pipe owner rather
than leaking `micromax-process-stdin`. A descendant that redirects all three
standard descriptors is not a capture owner and is deliberately left alive,
even when it shares the launched process group with a different pipe holder.

Capture threads now have stable Micromax names, all joins share one absolute
drain deadline instead of multiplying a timeout per thread, and timeout/output
teardown uses a short escalation grace. The forceful fallback calls
`Popen.kill()` rather than assuming a POSIX `SIGKILL` constant exists on every
host.

## Filesystem-worker audit and refactor

The same audit found an inverse ordering in bounded filesystem workers. Several
paths joined a producer before receiving its `multiprocessing.Queue` result.
Python's multiprocessing guidance warns that joining a process which has queued
items can deadlock until those items are consumed because a feeder thread must
flush the pipe. Large but permitted file reads or directory results could thus
be reported as timeouts after the filesystem operation had already succeeded.

`stat`, access, batched stat, read, and list workers now share one narrow helper:

1. start the isolated worker;
2. receive one result under the operation's finite timeout;
3. reap the terminal producer, terminating it after a short post-result grace;
4. on timeout/crash/receive failure, terminate first and cancel local queue-join
   behavior; and
5. close queue and process handles on every path.

Worker targets already make their single `queue.put()` the terminal action, so
accepting a complete result before reaping does not publish an intermediate
filesystem state. Integration tests exercise pipe-sized reads/listings through
spawn; a fake context asserts receive-before-join ordering and verifies that a
broken result pipe terminates the worker and releases IPC handles.

## Primary sources

- Python subprocess documentation, including pipe deadlock, timeout cleanup,
  `start_new_session`, and Windows terminate/kill behavior:
  https://docs.python.org/3/library/subprocess.html
- Linux `pipe(7)` EOF and capacity semantics:
  https://man7.org/linux/man-pages/man7/pipe.7.html
- Python pidfd APIs used when both interpreter and kernel support them:
  https://docs.python.org/3/library/os.html#os.pidfd_open
  https://docs.python.org/3/library/signal.html#signal.pidfd_send_signal
- Linux pidfd process identity and signaling semantics:
  https://man7.org/linux/man-pages/man2/pidfd_open.2.html
  https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html
- Linux `/proc/<pid>/stat` field 22 start-time fallback identity:
  https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
- Python multiprocessing queue/deadlock guidance:
  https://docs.python.org/3/library/multiprocessing.html
- Microsoft Job Objects, child association, whole-job termination, and
  kill-on-close:
  https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
  https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
  https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information

## Deliberately narrow claims

- Exact capture-pipe holder discovery is Linux `/proc` evidence. Pidfd signaling
  depends on Python/kernel support; the start-time fallback narrows but cannot
  make numeric signaling atomic. Other POSIX hosts retain confirmed process-group
  cleanup; Windows still has direct-child ownership, not a tested Job Object
  implementation.
- Process construction remains outside the post-start deadline.
- Properly redirected background work is an intentional external effect and may
  outlive Micromax.
- Exact pipe ownership authorizes release of the capture resource; it is not a
  general descendant census or sandbox.
- Filesystem worker startup itself is not preempted. After startup, a dead
  producer is detected between short result polls rather than consuming the
  entire operation deadline. A Queue receive that has begun consuming an
  incomplete/corrupt frame is not made asynchronously interruptible.
- These boundaries do not filter syscalls, cap total host memory, survive
  interpreter corruption, or contain arbitrary native crashes.
