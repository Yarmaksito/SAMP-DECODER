/** Created by Yarmak — Discord: https://discord.gg/cRU3fMq7v5 */
import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { IncomingMessage, ServerResponse } from 'node:http'

const catalogDir = path.dirname(fileURLToPath(import.meta.url))
const cacheDir = path.resolve(catalogDir, '..', 'Linked_Cache')

function naturalName(name: string) {
  const match = name.match(/(\d+)$/)
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY
}

function listModels() {
  if (!fs.existsSync(cacheDir)) return []

  const files = fs.readdirSync(cacheDir)
  const txds = new Set(
    files
      .filter((file) => file.toLowerCase().endsWith('.txd'))
      .map((file) => file.slice(0, -4).toLowerCase()),
  )

  return files
    .filter((file) => file.toLowerCase().endsWith('.dff'))
    .map((file) => file.slice(0, -4))
    .filter((base) => txds.has(base.toLowerCase()))
    .sort((a, b) => {
      const na = naturalName(a)
      const nb = naturalName(b)
      if (na !== nb) return na - nb
      return a.localeCompare(b)
    })
}

function insideCache(filePath: string) {
  const rel = path.relative(cacheDir, filePath)
  return rel !== '' && !rel.startsWith('..') && !path.isAbsolute(rel)
}

function linkedCache(): Plugin {
  const attach = (server: {
    middlewares: {
      use: (
        path: string,
        handler: (
          req: IncomingMessage,
          res: ServerResponse,
          next: () => void,
        ) => void,
      ) => void
    }
  }) => {
    server.middlewares.use('/api/models', (_req, res) => {
      try {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ models: listModels() }))
      } catch (error) {
        res.statusCode = 500
        res.end(String(error))
      }
    })

    server.middlewares.use('/cache', (req, res, next) => {
      const rel = decodeURIComponent((req.url ?? '').split('?')[0]).replace(
        /^\/+/,
        '',
      )
      const filePath = path.resolve(cacheDir, rel)

      if (!insideCache(filePath) || !fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
        next()
        return
      }

      res.setHeader('Access-Control-Allow-Origin', '*')
      fs.createReadStream(filePath).pipe(res)
    })
  }

  return {
    name: 'linked-cache',
    configureServer: attach,
    configurePreviewServer: attach,
  }
}

export default defineConfig({
  plugins: [vue(), linkedCache()],
  server: {
    fs: {
      allow: [catalogDir, cacheDir],
    },
  },
})
