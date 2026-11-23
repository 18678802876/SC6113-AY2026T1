#my first DAPP v2

from flask import Flask, render_template, request, render_template_string

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    return render_template_string(PAGE, mode='home')

@app.route('/depositMoney', methods=['GET', 'POST'])
def deposit_money():
    return render_template_string(PAGE, mode='deposit')

@app.route('/storeMsg', methods=['GET', 'POST'])
def store_message():
    return render_template_string(PAGE, mode='message')

@app.after_request
def mobile_layout(response):
    if response.mimetype == 'text/html':
        html = response.get_data(as_text=True)
        html = html.replace('device=device-width', 'width=device-width')
        html = html.replace('</head>', MOBILE + '</head>')
        response.set_data(html)
    return response

MOBILE = '''<style>*{box-sizing:border-box}body{height:auto!important;min-height:100dvh;padding:16px!important}input,button{font-size:16px!important;min-height:46px}p{overflow-wrap:anywhere}.container{margin:auto;width:100%;max-width:520px}a{display:block;padding:14px;color:#075ac5}label{display:block;text-align:left;margin-top:16px}button:disabled{opacity:.5}</style>'''

PAGE = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SC6106 DApp</title><link rel="stylesheet" href="{{url_for('static',filename='styles.css')}}"></head><body><main class="container">
<h2>{{ 'Main' if mode == 'home' else 'Store Message' if mode == 'message' else 'Deposit Money' }}</h2>
{% if mode == 'home' %}
<a href="/transferMoney">Transfer Money</a><a href="/depositMoney">Deposit Money</a><a href="/storeMsg">Store Message</a><a href="/">Exit</a>
{% else %}
<p>Sepolia test network. On mobile, open this page in MetaMask's browser.</p>
<button id="connect" onclick="connectWallet()">Connect Wallet</button>
{% if mode == 'message' %}<label for="value">Message</label><input id="value" placeholder="Enter message"><button class="action" onclick="writeValue()">Set Message</button><button class="action" onclick="readValue()">Get Message</button>
{% else %}<label for="value">Deposit amount (Sepolia ETH)</label><input id="value" inputmode="decimal" placeholder="0.01"><p>Deposit contract: <span id="address"></span></p><button class="action" onclick="writeValue()">Deposit Money</button><button class="action" onclick="readValue()">View Transaction</button>{% endif %}
<p id="output" role="status"></p><a href="/main">Main</a>
<script src="https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.umd.min.js"></script>
<script>
const mode={{mode|tojson}};
const address=mode==='message'?'0xd8e769b2bcc32a597f88cda7437aa8fd62d68b63':'0xd4cf9e66981989f344d1d175ba5608727e7bf968';
const abi=mode==='message'?['function setMessage(string _message)','function getMessage() view returns (string)']:['function deposit_money(address _depositor,uint256 _amount) payable','function transaction() view returns(address,uint256)'];
let provider,signer,contract,busy=false;
const output=text=>document.getElementById('output').textContent=text;
if(document.getElementById('address'))document.getElementById('address').textContent=address;
async function setup(){
 if(!window.ethereum)throw Error('Open this page in MetaMask mobile browser, or install MetaMask on desktop.');
 if(await ethereum.request({method:'eth_chainId'})!=='0xaa36a7')await ethereum.request({method:'wallet_switchEthereumChain',params:[{chainId:'0xaa36a7'}]});
 provider=new ethers.providers.Web3Provider(window.ethereum);await provider.send('eth_requestAccounts',[]);signer=provider.getSigner();
 if(await provider.getCode(address)==='0x')throw Error('Contract is not deployed at this address on Sepolia. Check the course contract address.');
 contract=new ethers.Contract(address,abi,signer);
 document.getElementById('connect').textContent='Connected: '+(await signer.getAddress()).slice(0,8)+'…';
}
async function connectWallet(){try{await setup();output('Wallet connected!')}catch(e){output(e.reason||e.message)}}
async function writeValue(){if(busy)return;busy=true;document.querySelectorAll('.action').forEach(b=>b.disabled=true);try{
 await setup();const value=document.getElementById('value').value;
 let tx;if(mode==='message'){if(!value.trim())throw Error('Enter a message.');output('Confirm in MetaMask…');tx=await contract.setMessage(value)}else{
 const wei=ethers.utils.parseEther(value.trim());if(wei.lte(0))throw Error('Enter a positive amount.');output('Confirm the ETH deposit in MetaMask…');tx=await contract.deposit_money(await signer.getAddress(),wei,{value:wei});}
 output('Submitted: '+tx.hash);await tx.wait();output('Confirmed: '+tx.hash);
 }catch(e){output(e.reason||e.message)}finally{busy=false;document.querySelectorAll('.action').forEach(b=>b.disabled=false)}}
async function readValue(){try{await setup();if(mode==='message')output('Stored Message: '+await contract.getMessage());else{const result=await contract.transaction();output('Depositor: '+result[0]+' | Amount (raw contract units): '+result[1].toString())}}catch(e){output(e.reason||e.message)}}
if(window.ethereum){ethereum.on('accountsChanged',()=>{signer=null;contract=null;output('Account changed. Reconnect wallet.')});ethereum.on('chainChanged',()=>{signer=null;contract=null;output('Network changed. Reconnect to Sepolia.')})}
</script>{% endif %}</main></body></html>'''

@app.route("/transferMoney",methods=["GET","POST"])
def transferMoney():
    return(render_template("transferMoney.html"))

if __name__ == "__main__":
    app.run()


