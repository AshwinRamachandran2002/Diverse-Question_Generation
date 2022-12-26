import dotenv from 'dotenv-safe'
import { oraPromise } from 'ora'
import { ChatGPTAPI, getOpenAIAuth } from '../src'
import * as employee from '../../469_metadata.json'

dotenv.config()

async function main() {
  
  const email = process.env.OPENAI_EMAIL
  const password = process.env.OPENAI_PASSWORD

  const authInfo = await getOpenAIAuth({
    email,
    password,
    // isGoogleLogin: true
  })

  const api = new ChatGPTAPI({ ...authInfo })
  await api.initSession()
  
  let prompt = 'given a product description, i want you to generate FAQs for it just like amazon from customer point of view'

  let res = await oraPromise(api.sendMessage(prompt), {
    text: prompt
  })

  console.log('\n' + res.response + '\n')

  
  for (let i=0; i < employee.default.length; i++) {

      await new Promise(r => setTimeout(r, (i+10) * 10000))
      prompt = 'Give me 10 FAqs for the following description from cutomer pov ' + employee.default[i].desc

      res = await oraPromise(
        api.sendMessage(prompt, {
          conversationId: res.conversationId,
          parentMessageId: res.messageId
        }),
        {
          text: prompt
        }
      )
  
      console.log('\n' + res.response + '\n')
  }
  
  await api.closeSession()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})