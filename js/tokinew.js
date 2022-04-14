window.addEventListener('DOMContentLoaded', () => {
    // prepare for search
    let contentJSON = null;

    let url = window.location.href
    let items = document.getElementsByClassName('menu-item-link')
    for (let item of items) {
        if(item.href === url)
            item.style.color = '#607d8b'
    }

    let search = document.querySelector('.search')
    let search_input = document.querySelector('.search-input')

    search.onclick = function(e){
        if (contentJSON == null)
            fetch('../../../../../../../content.json').then(res => res.json()).then(json => contentJSON = json)
        search.style.display = 'none'
        search_input.style.display = 'block'
        search_input.focus()
    }

    search_input.onblur = function(e){
        search_input.style.display = 'none'
        search.style.display = 'block'
    }

    function matcher(post, regExp) {
        // 匹配优先级：title > tags > text
        return regExp.test(post.title) || post.tags.some(function(tag) {
            return regExp.test(tag.name);
        }) || regExp.test(post.text);
    }

    render = function(result){
        if (result.length == 0) {
            document.querySelector('.search-items').innerHTML = ''
            document.querySelector('main').style.removeProperty('display')
        } else {
            let items = ''
            result.forEach(post => {
                let title = post.title
                let date = post.date
                let path = '../../../../../../../'+post.path
                date = new Date(date)
                date = date.toLocaleDateString()
               let item = `<li class='post-item'> \
                <span class='date'>${date}</span> \
                <a class='title' href='${path}'>${title}</a> \
              </li>`
              items += item
            });
            
           items = `<section class='archive'>
            <ul class='post-archive'>
                ${items}
            </ul>
          </section>`
          document.querySelector('.search-items').innerHTML = items
          document.querySelector('main').style.display = 'none'
        }
    }

    search_input.addEventListener('input', function(){
        if (search_input.value != '') {
            let regExp = new RegExp(search_input.value.replace(/[ ]/g, '|'), 'gmi')
            let result = contentJSON.filter(post => matcher(post, regExp))
            render(result)
        } else {
            document.querySelector('.search-items').innerHTML = ''
            document.querySelector('main').style.removeProperty('display')
        }
    })

    let codeBlocks = document.getElementsByTagName('pre')
    for (let block of codeBlocks) {
        block.addEventListener('dblclick', function(e){
            if (document.body.createTextRange) {
                let range = document.body.createTextRange();
                range.moveToElementText(block);
                range.select();
            } else if (window.getSelection) {
                let selection = window.getSelection();
                let range = document.createRange();
                range.selectNodeContents(block);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        })
    }
    
})