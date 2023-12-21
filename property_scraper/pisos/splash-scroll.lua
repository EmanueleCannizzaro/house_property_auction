function main(splash)
  local num_scrolls = 2
  local scroll_delay = 5

  assert(splash:go(splash.args.url))
  -- assert(splash:wait(0.5))

  local scroll_to = splash:jsfunc("window.scrollTo")
  local get_body_height = splash:jsfunc(
    "function() {return document.body.scrollHeight}"
  )

  for _ = 1, num_scrolls do
      scroll_to(0, get_body_height())
      splash:wait(scroll_delay)
  end

  return {
        html = splash:html()
       }
end