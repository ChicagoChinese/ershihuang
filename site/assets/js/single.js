function main() {
  const corrections = document.querySelectorAll('.correction')
  for (let correction of corrections) {
    const parent = correction.parentNode
    const original = parent.querySelector('.original')

    const button = document.createElement('button')
    button.innerText = 'Show correction'
    button.onclick = () => {
      original.classList.add('strikethrough')
      correction.classList.add('show')
      parent.removeChild(button)
    }
    parent.insertBefore(button, correction)
  }
}

main()
