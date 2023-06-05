// Script to export content from DeepL translation page
(function() {
  const textareas = document.querySelectorAll('d-textarea')
  const getLines = (index) => textareas[index].innerText.split('\n\n').map(line => line.trim())
  const lines1 = getLines(0)
  const lines2 = getLines(1)

  let output = []
  for (let i=0; i < lines1.length; i++) {
    if (lines1[i] === '') {
      output.push('')
    } else {
      output.push(lines1[i])
      output.push(lines2[i])
    }
  }
  console.log(output.join('\n'))
})()
