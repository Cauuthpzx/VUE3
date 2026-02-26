import { onUnmounted } from 'vue'

export function useApi() {
  const controllers = []

  function createSignal() {
    const controller = new AbortController()
    controllers.push(controller)
    return controller.signal
  }

  onUnmounted(() => {
    controllers.forEach((c) => c.abort())
  })

  return { createSignal }
}
