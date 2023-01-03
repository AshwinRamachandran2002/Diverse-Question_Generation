import dotenv from 'dotenv-safe'
import { oraPromise } from 'ora'

import { ChatGPTAPIBrowser } from '../src'
import * as employee from '../../469_metadata.json'
import * as fs from 'fs';

dotenv.config()

/**
 * Demo CLI for testing conversation support.
 *
 * ```
 * npx tsx demos/demo-conversation-browser.ts
 * ```
 */
async function main() {
  const email = process.env.OPENAI_EMAIL
  const password = process.env.OPENAI_PASSWORD

  const api = new ChatGPTAPIBrowser({
    email,
    password,
    debug: false,
    minimize: true
  })
  await api.initSession()
  
  for (let i=0; i < employee.default.length; i++) {
    
    let prompt = 'given a product description, i want you to generate diverse set of FAQs for it just like amazon from customer point of view'
    
    let res = await oraPromise(api.sendMessage(prompt), {
      text: prompt
    })
    
    const noFAQs = '10'
    console.log('\n' + res.response + '\n')
    
    prompt = 'Give me '+ noFAQs +' diverse good quality FAqs for the following description from customers perspective. ' + employee.default[i].desc + '. just a simple list of questions, no need of answers or additional text'
    
    res = await oraPromise(
      api.sendMessage(prompt, {
        conversationId: res.conversationId,
        parentMessageId: res.messageId
      }),
      {
        text: prompt
      }
    )
   
    // console.log('\n' + res.response + '\n')
    
    employee.default[i]['chatgptQuestions'] = []
    let answers = res.response.split('\n')
    for (let j=2; j < answers.length; j++) {
      employee.default[i]['chatgptQuestions'].push(answers[j].substring(3))
    }
    var json = JSON.stringify(employee.default[i]);
    fs.appendFile('../469_metadata_chatgpt.json', json, function(err) {
      if (err) throw err;
      // console.log('complete');
    });
  }
    
  await api.closeSession()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
