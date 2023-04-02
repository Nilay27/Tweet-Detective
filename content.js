( function () {
  let messageAppended = false;

  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log("Message received from background script: " + request.message)
    console.log("sender: ", sender)
    if (request.message === "append-message" ) {
      // Get the tweet element
      const tweetElement = document.querySelector(`a[href="${request.url}"]`);
      console.log(tweetElement)
      console.log(request.url)
      if (tweetElement) {
        const elementContainer = tweetElement.parentElement.parentElement
        const existingMessage = elementContainer.querySelector('.my-message');
        
        // Create a new element to display the likes count
        let resultMessage = document.createElement("div");
        resultMessage = applyCSS(resultMessage);
        resultMessage.classList.add('my-message'); // add a class to the message element
        if(request.result===1){
          resultMessage.innerText = `Strongly human generated`;
          resultMessage.style.color = "green";
        }
        else if(request.result===0.6){
          resultMessage.innerText = `Likely AI generated`;
          resultMessage.style.color = "yellow";
        }
        else{
          resultMessage.innerText = `Strongly AI generated`;
          resultMessage.style.color = "red";
        }
        
        resultMessage.style.alignContent = "center";
        
        /// If there is an existing message, replace it with the new one
        if (existingMessage) {
          elementContainer.replaceChild(resultMessage, existingMessage);
        } else {
          // Insert the new element after the like button
          elementContainer.insertBefore(resultMessage, tweetElement.nextSibling);
        }
        if(!messageAppended){
          messageAppended = true;
        }
        else{
          console.log("Message already appended for this tweet.");
        }
      }
      else{
        console.log("No tweet element found.");
      }
      messageAppended = false; // reset the variable for the next tweet
    }
  });
})();

function applyCSS(resultMessage){
  resultMessage.style.border = "0 solid black";
  resultMessage.style.boxSizing = "border-box";
  resultMessage.style.color = "rgba(0,0,0,1.00)";
  // resultMessage.style.display = "inline";
  resultMessage.style.font = "14px -apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif";
  resultMessage.style.marginBottom = "0px";
  resultMessage.style.marginLeft = "0px";
  resultMessage.style.marginRight = "0px";
  resultMessage.style.marginTop = "0px";
  resultMessage.style.paddingBottom = "0px";
  resultMessage.style.paddingLeft = "0px";
  resultMessage.style.paddingRight = "0px";
  resultMessage.style.paddingTop = "0px";
  resultMessage.style.whiteSpace = "pre-wrap";
  resultMessage.style.wordWrap = "break-word";
  resultMessage.style.alignItems = "center";
  return resultMessage;
}