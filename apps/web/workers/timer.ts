// Timer Web Worker
// Posts 'tick' messages every 250ms with current time
// The UI uses this to compute remaining time from targetEpochMs

let intervalId: ReturnType<typeof setInterval> | null = null;

self.onmessage = (e: MessageEvent) => {
  const { type } = e.data;

  if (type === "start") {
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(() => {
      self.postMessage({ type: "tick", now: Date.now() });
    }, 250);
  }

  if (type === "stop") {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }
};
