const { Readability } = require("@mozilla/readability");
const { JSDOM } = require("jsdom");

let html = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (html += chunk));
process.stdin.on("end", () => {
  try {
    const dom = new JSDOM(html, { url: process.argv[2] });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();
    if (!article) {
      console.log(JSON.stringify({ error: "Readability could not parse" }));
    } else {
      console.log(JSON.stringify({ content: article.content, title: article.title }));
    }
  } catch (e) {
    console.log(JSON.stringify({ error: e.message }));
  }
});
