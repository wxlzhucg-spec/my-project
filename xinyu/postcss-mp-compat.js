// PostCSS plugin to strip CSS rules incompatible with WeChat Mini Program WXSS
// Compatible with both PostCSS 7 and 8
module.exports = function postcssMpCompat() {
  return function(css) {
    css.walkRules(function(rule) {
      var sel = rule.selector
      // Remove rules with * (WXSS does not support it)
      // Note: ::before and ::after ARE supported in modern WXSS
      if (sel.indexOf('*') !== -1) {
        rule.remove()
        return
      }
      // Remove CSS custom properties (--tw-* etc)
      rule.walkDecls(function(decl) {
        if (decl.prop.indexOf('--') === 0) {
          decl.remove()
        }
      })
      // Remove empty-value declarations (e.g. --tw-pan-x: ;)
      rule.walkDecls(function(decl) {
        if (decl.value.trim() === '') {
          decl.remove()
        }
      })
      // Remove rule if it became empty
      if (rule.nodes.length === 0) {
        rule.remove()
      }
    })
    css.walkAtRules(function(atRule) {
      // Remove @layer (WXSS does not support it)
      if (atRule.name === 'layer') {
        atRule.remove()
      }
    })
  }
}
