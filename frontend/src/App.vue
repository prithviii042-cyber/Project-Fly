<template>
  <router-view />
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0f0f0f;
  color: #f0f0f0;
  min-height: 100vh;
}

/* Shared button styles */
.btn-primary {
  background: #3a7bd5; color: #fff; border: none;
  border-radius: 8px; padding: 9px 18px; font-size: 14px;
  cursor: pointer; font-weight: 500; text-decoration: none;
  display: inline-block; transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #2d63b0; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost {
  background: transparent; color: #aaa;
  border: 1px solid #333; border-radius: 8px;
  padding: 9px 18px; font-size: 14px; cursor: pointer;
  text-decoration: none; display: inline-block; transition: all 0.2s;
}
.btn-ghost:hover { border-color: #555; color: #f0f0f0; }
</style>
