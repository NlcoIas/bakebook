"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// IndexedDB helpers for timer persistence
const DB_NAME = "bakebook-timers";
const STORE_NAME = "timers";

interface TimerEntry {
  key: string; // bake:{bakeId}:step:{stepOrd}
  targetEpochMs: number;
  startedAt: number;
  pausedAt: number | null;
  label: string;
}

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      req.result.createObjectStore(STORE_NAME, { keyPath: "key" });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function saveTimer(entry: TimerEntry) {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  tx.objectStore(STORE_NAME).put(entry);
  db.close();
}

async function getTimer(key: string): Promise<TimerEntry | null> {
  const db = await openDB();
  return new Promise((resolve) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const req = tx.objectStore(STORE_NAME).get(key);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => resolve(null);
    db.close();
  });
}

async function deleteTimer(key: string) {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  tx.objectStore(STORE_NAME).delete(key);
  db.close();
}

export function useTimer(bakeId: string, stepOrd: number, durationSeconds: number | null) {
  const [remaining, setRemaining] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const workerRef = useRef<Worker | null>(null);
  const timerKey = `bake:${bakeId}:step:${stepOrd}`;

  // Restore timer on mount
  useEffect(() => {
    getTimer(timerKey).then((entry) => {
      if (entry && !entry.pausedAt) {
        const now = Date.now();
        const rem = Math.max(0, entry.targetEpochMs - now);
        if (rem > 0) {
          setRemaining(Math.ceil(rem / 1000));
          setIsRunning(true);
        } else {
          setIsDone(true);
          setRemaining(0);
        }
      }
    });
  }, [timerKey]);

  // Web Worker tick loop
  useEffect(() => {
    if (!isRunning) return;

    const worker = new Worker(new URL("../workers/timer.ts", import.meta.url));
    workerRef.current = worker;

    worker.onmessage = (e) => {
      if (e.data.type === "tick") {
        getTimer(timerKey).then((entry) => {
          if (!entry) return;
          const rem = Math.max(0, entry.targetEpochMs - e.data.now);
          const secs = Math.ceil(rem / 1000);
          setRemaining(secs);
          if (secs <= 0 && !isDone) {
            setIsDone(true);
            setIsRunning(false);
            worker.postMessage({ type: "stop" });
            fireNotification(entry.label);
          }
        });
      }
    };

    worker.postMessage({ type: "start" });

    return () => {
      worker.postMessage({ type: "stop" });
      worker.terminate();
      workerRef.current = null;
    };
  }, [isRunning, timerKey, isDone]);

  // Recompute on visibility change (returning from background)
  useEffect(() => {
    const handler = () => {
      if (document.visibilityState === "visible" && isRunning) {
        getTimer(timerKey).then((entry) => {
          if (entry) {
            const rem = Math.max(0, entry.targetEpochMs - Date.now());
            setRemaining(Math.ceil(rem / 1000));
            if (rem <= 0) {
              setIsDone(true);
              setIsRunning(false);
            }
          }
        });
      }
    };
    document.addEventListener("visibilitychange", handler);
    return () => document.removeEventListener("visibilitychange", handler);
  }, [isRunning, timerKey]);

  const start = useCallback(async () => {
    if (!durationSeconds) return;
    const now = Date.now();
    const target = now + durationSeconds * 1000;
    await saveTimer({
      key: timerKey,
      targetEpochMs: target,
      startedAt: now,
      pausedAt: null,
      label: `Step ${stepOrd} timer`,
    });
    setRemaining(durationSeconds);
    setIsRunning(true);
    setIsDone(false);
  }, [timerKey, durationSeconds, stepOrd]);

  const reset = useCallback(async () => {
    await deleteTimer(timerKey);
    setRemaining(null);
    setIsRunning(false);
    setIsDone(false);
    if (workerRef.current) {
      workerRef.current.postMessage({ type: "stop" });
    }
  }, [timerKey]);

  return { remaining, isRunning, isDone, start, reset };
}

function fireNotification(label: string) {
  if (!("Notification" in window)) return;
  if (Notification.permission === "granted") {
    // vibrate is part of the Notification API spec but not in TS types
    const opts: NotificationOptions & { vibrate?: number[] } = {
      body: label,
      requireInteraction: true,
      vibrate: [200, 100, 200, 100, 400],
    };
    new Notification("Timer done!", opts);
  }
}

export function formatTimer(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}
