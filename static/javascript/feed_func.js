// delete event announcement
const closeIcon = document.querySelector('.close');
if (closeIcon) {
    closeIcon.addEventListener('click', function () {
        const announcementDiv = document.querySelector('.announcement');
        announcementDiv.remove();
    });
}
for (let settingsIcon of document.querySelectorAll('img[alt="Settings"]')) {
    let the_id = settingsIcon.getAttribute('id')
    const settingsOptions = document.querySelector('div[for="so' + the_id + '"]');

    settingsIcon.addEventListener('click', function () {
        settingsOptions.style.display = 'block';
    });

    document.addEventListener('click', function (event) {
        const isClickInside = settingsIcon.contains(event.target) || settingsOptions.contains(event.target);
        if (!isClickInside) {
            settingsOptions.style.display = 'none';
        }
    });
}
// for each button with for as like
for (let button of document.querySelectorAll('a[for^="like"]')) {
    let button_id = button.getAttribute('id')
    let timer
    button.addEventListener('click', event => {
        if (event.detail === 1) {
            timer = setTimeout(() => {
                // single click action
                // if the button is green, make it white and change the text to decrement the likes
                if (document.getElementById(button_id + "img").src.includes('/static/images/likeButton_red.png')) {
                    document.getElementById(button_id + "img").src = '/static/images/likeButton_default.png';
                    document.getElementById(button_id + "t").innerHTML = parseInt(document.getElementById(button_id + "t").innerHTML) - 1 + " Likes"
                    var request = new XMLHttpRequest()
                    request.open("GET", "/feed/remove_like/" + button_id, true)
                    request.send()
                } // if the button is red, make it white and change the text to increment the likes
                else if (document.getElementById(button_id + "img").src.includes('/static/images/likeButton_grey.png')) {
                    document.getElementById(button_id + "img").src = '/static/images/likeButton_default.png';
                    document.getElementById(button_id + "t").innerHTML = parseInt(document.getElementById(button_id + "t").innerHTML) + 1 + " Likes"
                    var request = new XMLHttpRequest()
                    request.open("GET", "/feed/like/" + button_id, true)
                    request.send()
                } // if the button is white, make it green and change the text to increment the likes
                else {
                    document.getElementById(button_id + "img").src = '/static/images/likeButton_red.png';
                    document.getElementById(button_id + "t").innerHTML = parseInt(document.getElementById(button_id + "t").innerHTML) + 1 + " Likes"
                    var request = new XMLHttpRequest()
                    request.open("GET", "/feed/like/" + button_id, true)
                    request.send()
                }
            }, 200)
        }
    })
    button.addEventListener('dblclick', event => {
        clearTimeout(timer)
        // double click action
        // if the button is green, make it red and change the text to decrement the likes twice
        if (document.getElementById(button_id + "img").src.includes('/static/images/likeButton_red.png')) {
            document.getElementById(button_id + "t").innerHTML = parseInt(document.getElementById(button_id + "t").innerHTML) - 2 + " Likes"
        } // if the button is white, make red and decrement the likes once
        else if (document.getElementById(button_id + "img").src.includes('/static/images/likeButton_default.png')) {
            document.getElementById(button_id + "t").innerHTML = parseInt(document.getElementById(button_id + "t").innerHTML) - 1 + " Likes"
        } // if red, do nothing
        document.getElementById(button_id + "img").src = '/static/images/likeButton_grey.png';
        var request = new XMLHttpRequest()
        request.open("GET", "/feed/dislike/" + button_id, true)
        request.send()
    })
}