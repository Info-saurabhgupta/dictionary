const input = document.getElementById("word");
const suggestionsBox = document.getElementById("suggestions");

let currentFocus = -1;

// Live Suggestion
input.addEventListener("input", async function() {
    const term = this.value;
    if (!term) {
        suggestionsBox.innerHTML = "";
        return;
    }

    const res = await fetch(`/suggest?term=${term}`);
    const data = await res.json();

    suggestionsBox.innerHTML = "";
    currentFocus = -1;

    data.forEach(word => {
        const div = document.createElement("div");
        div.classList.add("suggestion-item");
        div.innerText = word;

        div.onclick = function() {
            input.value = word;
            suggestionsBox.innerHTML = "";
            searchWord();
        };

        suggestionsBox.appendChild(div);
    });
});

// Keyboard Navigation
input.addEventListener("keydown", function(e) {
    const items = document.querySelectorAll(".suggestion-item");

    if (e.key === "ArrowDown") {
        currentFocus++;
        addActive(items);
    } else if (e.key === "ArrowUp") {
        currentFocus--;
        addActive(items);
    } else if (e.key === "Enter") {
        e.preventDefault();
        if (currentFocus > -1) {
            items[currentFocus].click();
        } else {
            searchWord();
        }
    }
});

function addActive(items) {
    if (!items.length) return;

    items.forEach(item => item.classList.remove("active"));

    if (currentFocus >= items.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = items.length - 1;

    items[currentFocus].classList.add("active");
}

// SEARCH
async function searchWord() {
    const word = input.value;
    suggestionsBox.innerHTML = "";

    const response = await fetch(`/search?word=${word}`);
    const data = await response.json();

    let html = `<div class="word-title">${data.word.toUpperCase()}</div>`;

    if (data.english) {

        if (data.english.phonetic) {
            html += `<div class="phonetic">/${data.english.phonetic.replace(/\//g,"")}/</div>`;
        }

        if (data.english.uk_audio) {
            html += `<button class="audio-btn" onclick="playAudio('${data.english.uk_audio}')">🇬🇧 UK</button>`;
        }

        if (data.english.us_audio) {
            html += `<button class="audio-btn" onclick="playAudio('${data.english.us_audio}')">🇺🇸 US</button>`;
        }

        html += `<div class="section"><h3>English Meaning</h3>`;

        data.english.meanings.forEach(m => {
            html += `<b>${m.partOfSpeech}</b>`;
            m.definitions.forEach((d, i) => {
                html += `<div class="definition">${i+1}. ${d.definition}</div>`;
                if (d.example) {
                    html += `<div class="example">Example: ${d.example}</div>`;
                    html += `<div class="example-hi">Hindi: ${d.example_hi || ""}</div>`;
                }
            });
        });

        html += `</div>`;
    }

    if (data.hindi && data.hindi.length > 0) {
        html += `<div class="section"><h3>Hindi Meaning</h3>`;
        data.hindi.forEach((h, i) => {
            html += `<div class="definition">${i+1}. ${h}</div>`;
        });
        html += `</div>`;
    }

    document.getElementById("result").innerHTML = html;
}

function playAudio(url) {
    new Audio(url).play();
}