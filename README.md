# Staffeli — DIKU Support Tools for Canvas LMS

"Staffeli" is Danish for "easel" — a support frame for holding up a canvas.

![An Easel](logo.jpg
  "Image license: CC0; Source: https://pixabay.com/en/art-painting-modern-art-mural-1027828/")

These tools leverage the [Canvas LMS REST
API](https://canvas.instructure.com/doc/api/index.html) to create a more
pleasant environment for working with [Absalon](https://absalon.ku.dk/).

## Contributing

We use a tab-width of 4 spaces, with tabs expanded to spaces.

### `vim`

Add this to your `~/.vimrc`:

```
au BufNewFile,BufRead /path/to/Staffeli/* set expandtab tabstop=4
```
