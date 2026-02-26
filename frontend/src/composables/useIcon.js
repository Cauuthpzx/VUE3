const iconModules = import.meta.glob('@/assets/icons/**/*.svg', {
  eager: true,
  query: '?url',
  import: 'default',
})

const iconMap = new Map()

for (const [path, url] of Object.entries(iconModules)) {
  const fileName = path.split('/').pop().replace('.svg', '')
  iconMap.set(fileName, url)
}

export function useIcon() {
  function getIconUrl(name) {
    return iconMap.get(name) || null
  }

  function hasIcon(name) {
    return iconMap.has(name)
  }

  function listIcons(category = null) {
    if (!category) {
      return [...iconMap.keys()]
    }
    const prefix = `assets/icons/${category}/`
    return Object.entries(iconModules)
      .filter(([path]) => path.includes(prefix))
      .map(([path]) => path.split('/').pop().replace('.svg', ''))
  }

  function listCategories() {
    const categories = new Set()
    for (const path of Object.keys(iconModules)) {
      const parts = path.split('/')
      const iconsIdx = parts.indexOf('icons')
      if (iconsIdx >= 0 && parts[iconsIdx + 1]) {
        categories.add(parts[iconsIdx + 1])
      }
    }
    return [...categories]
  }

  return { getIconUrl, hasIcon, listIcons, listCategories }
}
