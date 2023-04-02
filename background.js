const token = "YOUR_TWITTER_BEARER_TOKEN";

function cleanTweets(tweet) {
  const tweetWithoutHashtagsAndLinks = tweet.replace(/#[\w\d]+|https?:\/\/\S+/g, '');
  let finalTweet = tweetWithoutHashtagsAndLinks.replace(/\n|\r/g, '');
  finalTweet = finalTweet.toLowerCase();
  if (finalTweet.length > 100) {
    return finalTweet;
  } else {
    return null;
  }
}

async function tweetLookup (tweetId){
    console.log("entered tweetLookup", tweetId)
    const url = "https://api.twitter.com/2/tweets";

    // These are the parameters for the API request
    // specify Tweet IDs to fetch, and any additional fields that are required
    // by default, only the Tweet ID and text are returned
    const params = {
        "ids": tweetId,
        "tweet.fields": "author_id",
        "user.fields": "created_at"
      };
      
      const queryString = new URLSearchParams(params).toString();
      
      const urlWithParams = `${url}?${queryString}`;
      
      const res = await fetch(urlWithParams, {
        headers: {
          "User-Agent": "v2TweetLookupJS",
          "Authorization": `Bearer ${token}`,
        },
      });

      const result = await res.json();
      
      
      

    if (result.data) {
        return {userId: result.data[0].author_id, text: result.data[0].text};
    } else {
        throw new Error('Unsuccessful request');
    }
}

async function getOriginalAndRandomTweets(tweetId) {
    const {userId, text} = await tweetLookup(tweetId)
    const endpointURL = `https://api.twitter.com/2/users/${userId}/tweets`;
    /// These are the parameters for the API request
    // specify Tweet IDs to fetch, and any additional fields that are required
    // by default, only the Tweet ID and text are returned
    
    // start time = 1 month back from now
    // end time = now
    // max_results = 5
    // exclude = replies, retweets
    start_time = new Date()
    start_time.setMonth(start_time.getMonth() - 11)
    start_time = start_time.toISOString()
    end_time = new Date("December 31, 2022");
    end_time = end_time.toISOString()
    console.log("start time: ", start_time)
    const params = {
        "max_results": 10,
        "exclude": "replies,retweets",
        "start_time": start_time,
        "end_time": end_time,
    }
    const queryString = new URLSearchParams(params).toString();
    
    const urlWithParams = `${endpointURL}?${queryString}`;
      

    const res = await fetch(urlWithParams, {
        method: 'GET',
        headers: {
          'User-Agent': 'v2UserTweetsJS',
          'Authorization': `Bearer ${token}`
        },
      });

      const result = await res.json();
      var tweetData = []
        if (result.data) {
            tweetData = result.data
        } else{
            console.log("not enough tweets found till dec 2022, fetching recent tweets ...")
            const newParams = {"max_results": 10,
                "exclude": "replies,retweets",
                "start_time": start_time,
            }
            const queryString = new URLSearchParams(newParams).toString();
    
            const urlWithParams = `${endpointURL}?${queryString}`;
            

            const res = await fetch(urlWithParams, {
                method: 'GET',
                headers: {
                'User-Agent': 'v2UserTweetsJS',
                'Authorization': `Bearer ${token}`
                },
            });
            const result = await res.json();
            tweetData = result.data
        }

      console.log("fetched data : ", tweetData)
    
    if(tweetData.length < 5 ) {
            const result = ["not enough tweets found"]
            return result
        }
    else {
        // randomly pick 5 elements from it and append the text to the array, ensure no repetition
        const originalAndRandomTweets = []
        // tweet 1 will be original tweet
        originalAndRandomTweets.push(text)

        // others will be 5 random tweets
        while(originalAndRandomTweets.length < 6) {
            const randomIndex = Math.floor(Math.random() * tweetData.length)
            const randomTweet = tweetData[randomIndex]
            if(!originalAndRandomTweets.includes(randomTweet.text)) {
                originalAndRandomTweets.push(randomTweet.text)
            }
        }
        // ensure no individual tweet is more than 350 characters, if it is, only take first 280 characters
        originalAndRandomTweets.forEach((tweet, index) => {
            if(tweet.length > 350) {
                originalAndRandomTweets[index] = tweet.slice(0, 350)
            }
        })
        
        return {desiredTweets: originalAndRandomTweets, originalText: text}     
    } 
}
function getOpenAIPrompt(desiredTweets){
    // convert desiredTweets the following format: "tweet1: `${tweet1}`, tweet2: `${tweet2}`, tweet3: `${tweet3}`, tweet4: `${tweet4}`, tweet5: `${tweet5}`"
    const openAIInput = desiredTweets.reduce((acc, tweet, index) => {
        return acc + `tweet${index + 1}: ${tweet}, `
    }, "")

    const prompt = openAIInput + "->"

    return prompt
}

async function callOpenAIModel(desiredTweets, originalText) {
    const prompt = getOpenAIPrompt(desiredTweets)
    const res = await fetch(
        `https://api.openai.com/v1/completions`,
        {
            body: JSON.stringify(
            {
                "model": "ada:ft-personal-2023-03-28-17-52-51", 
                "prompt": prompt,
                "max_tokens": 2, 
            }),
            method: "POST",
            headers: {
                "content-type": "application/json",
                Authorization: "Bearer YOUR_OPEN_AI_TOKEN",
            },
        }
    )
    const result = await res.json();
    const resultText = result.choices[0].text
    // convert result text to number
    const resultNumberAnomaly = parseInt(resultText)
    const cleanTweet = cleanTweets(originalText)
    const promptForAIDetector = cleanTweet + " -> "
    console.log("calling AI detector model with prompt: ", promptForAIDetector)
    const resAIDetector = await fetch(
        `https://api.openai.com/v1/completions`,
        {
            body: JSON.stringify(
            {
                "model": "ada:ft-personal:ai-tweet-detector-1-2023-04-01-07-27-32",
                "prompt": promptForAIDetector,
                "max_tokens": 1,
            }),
            method: "POST",
            headers: {
                "content-type": "application/json",
                Authorization: "Bearer YOUR_OPEN_AI_TOKEN",
            }
        }
    )
    const resultAIDetector = await resAIDetector.json();
    const resultNumberAIDetector = parseInt(resultAIDetector.choices[0].text)

    console.log(" resAIDetector", resultNumberAIDetector)
    console.log("result from openai anomaly", resultNumberAnomaly)
    const resultNumber = score(resultNumberAIDetector, resultNumberAnomaly)
    return resultNumber
}

function score(resAIDetector, resAnomalyDetector) {
  if (resAIDetector == 0) {
    return 0;
  } else if (resAIDetector == 1 && resAnomalyDetector == 0) {
    return 0.6;
  } else if (resAIDetector == 1 && resAnomalyDetector == 1) {
    return 1;
  } else {
    throw new Error("Invalid input values");
  }
}





chrome.tabs.onUpdated.addListener(async(tabId, changeInfo, tab) => {
    var updatedUrl = changeInfo.url;
    if (updatedUrl) {
        console.log("onUpdateInfo", tabId)
        // last element of the array is the tweetId
        // get last element of the array
        const tweetId = updatedUrl.split("/")[updatedUrl.split("/").length - 1]
        // check if updatedUrl is of the form https://twitter.com/*/status/*
        if(updatedUrl.match(/https:\/\/twitter\.com\/[^\/]+\/status\/\d+/)) {
            console.log("tweetId: ", tweetId)
            const {desiredTweets, originalText} = await getOriginalAndRandomTweets(tweetId)
            if(desiredTweets.length > 5) {
                const result = await callOpenAIModel(desiredTweets, originalText)
                console.log("sending message to content script, tabId: ", tabId)
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ["content.js"],
                    });
                // remove https://twitter.com from updatedUrl using regex
                updatedUrl = updatedUrl.replace(/https:\/\/twitter\.com/, "")

                chrome.tabs.sendMessage(tabId, {message: "append-message", result: result, url: updatedUrl});
                
            }
        }

    }
});
