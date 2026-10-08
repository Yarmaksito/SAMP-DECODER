<template>
  <div class="app">
    <aside class="sidebar">
      <header class="brand">
        <h1>Yarmak's Suite</h1>
        <p class="stats">
          <a href="https://youtu.be/41qC3w3UUkU" target="_blank" rel="noreferrer">HIT 'EM UP</a>
          <a href="https://discord.gg/cRU3fMq7v5" target="_blank" rel="noreferrer">Discord</a>
          <span>{{ models.length }} models</span>
        </p>
      </header>

      <input
        v-model="query"
        class="search"
        type="search"
        placeholder="Search Linked_Cache..."
        spellcheck="false"
      />

      <div v-if="!models.length" class="empty-list">
        Linked_Cache is empty. Decode a SA:MP cache, then run <code>python linker.py</code>.
      </div>

      <div v-else class="model-list">
        <button
          v-for="name in filtered"
          :key="name"
          type="button"
          class="model-item"
          :class="{ active: selected === name }"
          @click="selectModel(name)"
        >
          {{ name }}
        </button>
        <p v-if="!filtered.length" class="empty-list">No matches.</p>
      </div>
    </aside>

    <main class="stage">
      <section v-if="selected" class="viewer">
        <div class="toolbar">
          <h2>{{ selected }}</h2>
          <div class="actions">
            <button type="button" class="btn ghost" :disabled="filteredIndex <= 0" @click="step(-1)">Prev</button>
            <button type="button" class="btn ghost" :disabled="filteredIndex >= filtered.length - 1" @click="step(1)">Next</button>
            <button type="button" class="btn" @click="downloadZip">Download ZIP</button>
          </div>
        </div>
        <div class="canvas-wrap">
          <div v-if="isLoading" class="overlay">Loading model...</div>
          <div v-else-if="error" class="overlay error">{{ error }}</div>
          <canvas ref="renderCanvas"></canvas>
        </div>
      </section>

      <section v-else class="placeholder">
        <pre class="ascii">
 __   __                    _
 \ \ / /_ _ _ __ _ __  __ _| |__
  \ V / _` | '__| '  \/ _` | / /
   | | (_| | |  | |\/| (_| |   \
   |_|\__,_|_|  |_|  |\__,_|_|\_\

   Created by Yarmak
   Discord: https://discord.gg/cRU3fMq7v5
        </pre>
        <p>Select a model from Linked_Cache to preview it in the browser.</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
/** Created by Yarmak — Discord: https://discord.gg/cRU3fMq7v5 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import type { SkinPreview } from './viewer.js'

const models = ref<string[]>([])
const query = ref('')
const selected = ref('')
const isLoading = ref(false)
const error = ref('')
const renderCanvas = ref<HTMLCanvasElement | null>(null)

let viewer: typeof import('./viewer.js') | null = null
let preview: SkinPreview | null = null
let loadSeq = 0

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return models.value
  return models.value.filter((name) => name.toLowerCase().includes(q))
})

const filteredIndex = computed(() => filtered.value.indexOf(selected.value))

onMounted(async () => {
  try {
    const res = await fetch('/api/models')
    const data = await res.json()
    models.value = Array.isArray(data.models) ? data.models : []
  } catch (err) {
    console.error('Failed to load catalog', err)
  }
})

onBeforeUnmount(() => {
  preview?.dispose()
  preview = null
})

const assetUrl = (name: string, ext: 'dff' | 'txd') =>
  `/cache/${encodeURIComponent(`${name}.${ext}`)}`

const selectModel = async (name: string) => {
  const seq = ++loadSeq
  selected.value = name
  isLoading.value = true
  error.value = ''

  await nextTick()
  if (!renderCanvas.value || seq !== loadSeq) return

  try {
    preview?.dispose()
    preview = null

    if (!viewer) viewer = await import('./viewer.js')
    const skinData = await viewer.prepareSkin(assetUrl(name, 'dff'), assetUrl(name, 'txd'), 'full')
    if (seq !== loadSeq) return

    preview = new viewer.SkinPreview(renderCanvas.value, 'full')
    preview.show(skinData)
  } catch (err) {
    if (seq !== loadSeq) return
    console.error('Failed to load 3D preview:', err)
    error.value = err instanceof Error ? err.message : 'Failed to load model'
  } finally {
    if (seq === loadSeq) isLoading.value = false
  }
}

const step = (delta: number) => {
  const next = filtered.value[filteredIndex.value + delta]
  if (next) void selectModel(next)
}

const downloadZip = async () => {
  if (!selected.value) return

  try {
    const [dffRes, txdRes] = await Promise.all([
      fetch(assetUrl(selected.value, 'dff')),
      fetch(assetUrl(selected.value, 'txd')),
    ])
    if (!dffRes.ok || !txdRes.ok) throw new Error('Asset request failed')

    const zip = new JSZip()
    zip.file(`${selected.value}.dff`, await dffRes.blob())
    zip.file(`${selected.value}.txd`, await txdRes.blob())
    saveAs(await zip.generateAsync({ type: 'blob' }), `${selected.value}.zip`)
  } catch (err) {
    console.error('Failed to zip:', err)
    error.value = 'Download failed'
  }
}
</script>

<style>
:root {
  --primary: #00ff88;
  --bg: #0a0a0a;
  --panel: #111;
  --border: #222;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: #fff;
  font-family: -apple-system, sans-serif;
  overflow: hidden;
}

.app {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 320px;
  background: var(--panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.brand h1 {
  color: var(--primary);
  margin: 20px 20px 6px;
  font-size: 1.4rem;
  text-transform: uppercase;
}

.stats {
  margin: 0 20px 16px;
  color: #666;
  font-size: 0.85rem;
  font-family: ui-monospace, monospace;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.stats a {
  color: inherit;
  text-decoration: none;
}

.search {
  margin: 0 16px 12px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  background: #0d0d0d;
  color: #fff;
  font-family: ui-monospace, monospace;
  border-radius: 4px;
}

.search:focus {
  outline: 1px solid var(--primary);
}

.model-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  background: var(--bg);
  scrollbar-width: thin;
  scrollbar-color: #333 var(--bg);
}

.model-list::-webkit-scrollbar {
  width: 8px;
}

.model-list::-webkit-scrollbar-track {
  background: var(--bg);
}

.model-list::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}

.model-list::-webkit-scrollbar-thumb:hover {
  background: #444;
}

.model-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 9px 20px;
  font-family: ui-monospace, monospace;
  font-size: 0.85rem;
  color: #ddd;
  background: transparent;
  border: 0;
  border-bottom: 1px solid #111;
  cursor: pointer;
}

.model-item:hover {
  background: #1a1a1a;
  color: var(--primary);
}

.model-item.active {
  background: rgba(0, 255, 136, 0.1);
  color: var(--primary);
  border-left: 3px solid var(--primary);
}

.empty-list {
  margin: 16px 20px;
  color: #777;
  font-size: 0.85rem;
  line-height: 1.4;
}

.empty-list code {
  color: var(--primary);
}

.stage {
  flex: 1;
  display: flex;
  min-width: 0;
}

.placeholder,
.viewer {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.placeholder {
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #888;
}

.ascii {
  color: var(--primary);
  background: #000;
  padding: 20px;
  border-radius: 5px;
  border: 1px solid var(--border);
  margin: 0;
}

.toolbar {
  padding: 16px 20px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.toolbar h2 {
  margin: 0;
  font-family: ui-monospace, monospace;
  color: #ddd;
  font-size: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  background: var(--primary);
  color: #000;
  border: none;
  padding: 8px 14px;
  font-weight: 700;
  border-radius: 4px;
  cursor: pointer;
}

.btn.ghost {
  background: #1a1a1a;
  color: #ddd;
  border: 1px solid var(--border);
}

.btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.canvas-wrap {
  flex: 1;
  position: relative;
  background: #222;
}

.overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--primary);
  font-family: ui-monospace, monospace;
  background: rgba(0, 0, 0, 0.8);
  padding: 10px 20px;
  border: 1px solid var(--primary);
  border-radius: 4px;
  z-index: 10;
}

.overlay.error {
  color: #ff6b6b;
  border-color: #ff6b6b;
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
