import { onUnmounted } from 'vue'

/**
 * Composable that provides AbortController-backed signal for API calls.
 * Automatically aborts all pending requests when the component unmounts.
 *
 * Usage:
 *   const { signal, abort, newSignal } = useAbortController()
 *   const { data } = await client.get('/api/data', { signal: newSignal() })
 */
export function useAbortController() {
  const controllers = new Set()

  function newSignal() {
    const controller = new AbortController()
    controllers.add(controller)
    return controller.signal
  }

  function abort() {
    controllers.forEach(c => c.abort())
    controllers.clear()
  }

  function removeCompleted(signal) {
    for (const c of controllers) {
      if (c.signal === signal) {
        controllers.delete(c)
        break
      }
    }
  }

  onUnmounted(() => {
    abort()
  })

  return { newSignal, abort, removeCompleted }
}
