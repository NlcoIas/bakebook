# M4 Issues

## 1. Service worker not implemented
**Problem**: Full offline caching requires a service worker (next-pwa or custom). Not implemented in this session.
**Impact**: PWA installs but doesn't work offline. Recipes require network.

## 2. PNG icons not generated
**Problem**: manifest.json references icon-192.png and icon-512.png but only icon.svg exists.
**Impact**: Some PWA installers may not find the icons. SVG works as fallback for most browsers.
