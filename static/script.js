var player;
function onYouTubeIframeAPIReady() {

  
}
/*
player = new YT.Player('player', {
  height: '420',
  width: '840',
  events: {
    'onReady': onPlayerReady
  }
});

player.loadVideoById(videoId);
*/


function displayLyrics(data) {
  const originalLyrics = data.original;
  var translatedLyrics = ''
  if ('English' in data) {
    translatedLyrics = data.English;
  }
  const originalLines = originalLyrics.split('\n');
  const translatedLines = translatedLyrics.split('\n');
  const container = $('#lyrics-container');

  // Clear previous content
  container.empty();
  console.log(translatedLines)
  if (translatedLines.length > 1) {
    var lineContainer = $('<div>').addClass('line-container');
    var checkbox = $('<input>').attr('type', 'checkbox').attr('id', `selectAll`).addClass('nonlyric-checkbox');
    var originalLabel = $('<label>').addClass('lyric-label original').attr('for', `selectAll`).text('select all');
    lineContainer.append(checkbox);
    lineContainer.append(originalLabel);
    container.append(lineContainer);
    document.getElementById('exportBtn').style.display = 'block';
    document.getElementById("selectAll").addEventListener("change", function() {
      var checkboxes = document.querySelectorAll(".lyric-checkbox");
      checkboxes.forEach(function(checkbox) {
          checkbox.checked = this.checked;
      }.bind(this));
    });
  }
  for(let i = 0; i < Math.min(originalLines.length); i++) {
      var trans = translatedLines[i] || '';
      lineContainer = $('<div>').addClass('line-container');
      checkbox = $('<input>').attr('type', 'checkbox').attr('id', `checkbox-${i}`).addClass('lyric-checkbox');
      originalLabel = $('<label>').addClass('lyric-label original').attr('for', `checkbox-${i}`).text(originalLines[i]);
      const translatedLabel = $('<label>').addClass('lyric-label translated').attr('for', `checkbox-${i}`).text(trans);

      if(originalLines[i].trim() === "" && trans.trim() == "") {checkbox = $('<span>').addClass('nonlyric-checkbox')}
      lineContainer.append(checkbox);
      lineContainer.append(originalLabel);
      lineContainer.append(translatedLabel);
      container.append(lineContainer);
  }
  
  
}



document.getElementById("exportBtn").addEventListener("click", function() {
  // Get all checkboxes
  var checkboxes = document.querySelectorAll(".lyric-checkbox");
  var selectedLines = [];

  // Use a set to track unique originalText values
  var seenOriginalTexts = new Set();

  checkboxes.forEach(function(checkbox, index) {
      if (checkbox.checked) {
          let lineContainer = checkbox.closest('.line-container');
          let originalText = lineContainer.querySelector('.original').innerText;
          let translatedText = lineContainer.querySelector('.translated').innerText;

          // Check if originalText is unique
          if (!seenOriginalTexts.has(originalText)) {
              seenOriginalTexts.add(originalText);
              // Format the data as CSV: "Original","Translated"
              selectedLines.push(`"${originalText}";"${translatedText}"`);
          }
      }
  });

  // Convert the array to a CSV string
  var csvContent = "data:text/csv;charset=utf-8," + selectedLines.join("\n");
  
  // Create a blob from the CSV string and make it downloadable
  var encodedUri = encodeURI(csvContent);
  var link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "anki_import.csv");
  document.body.appendChild(link);
  link.click();
});




function handleItemClick(query) {
  console.log("Clicked:", query);
  $.ajax({
    type: "POST",
    url: "/lyrics",
    data: JSON.stringify({ query: query }),
    contentType: "application/json; charset=utf-8",  // Set content type to JSON
    dataType: "json",
    success: function(response) {
        console.log("Success:", response.results);
        displayLyrics(response.results);
    },
    error: function(error) {
        console.error("Error:", error);
    }
    
});
}


  $(document).ready(function() {
    let previousQuery = '';

    $("#searchInput").on("keyup", function() {
      let query = $(this).val();
      if (query !== previousQuery) {  // Check if the input has changed
        previousQuery = query;

        if (query.length > 1) {
            $.ajax({
                type: "POST",
                url: "/search",
                data: JSON.stringify({ query: query }),
                contentType: "application/json; charset=utf-8",  // Set content type to JSON
                dataType: "json",
                success: function(response) {
                    let resultsList = $("#searchResults");
                    resultsList.empty();
                    if (response.results.length > 0) {
                      resultsList.show();
                      response.results.forEach(function(result) {
                        let li = $('<li></li>').text(result);
                        li.on('click', function() {
                            handleItemClick($(this).text());  // Call a function on click with the item's text
                        });
                        resultsList.append(li);
                    });
                      } else {
                          resultsList.hide();
                      }
                      
                },
                error: function(error) {
                    console.error("Error:", error);
                }
            });
        }
      }
    });



  // Optional: Hide results when clicked outside
  $(document).on('click', function(event) {
      if (!$(event.target).closest('#searchInput').length) {
          $('#searchResults').empty();
      }
  });
});


