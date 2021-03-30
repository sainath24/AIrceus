import {Moves} from "./moves.js"
import * as readline from "readline" 

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
   
  rl.question('', id => {
    console.log(JSON.stringify(Moves[id]));
    rl.close();
  });

// console.log(Moves[process.argv[2]])