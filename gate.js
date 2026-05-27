"use strict";
(function(){
  var SALT,B64_SALT,ITERATIONS;

  function init(){
    var gs=document.querySelector('script[data-salt]');
    if(!gs)return;
    B64_SALT=gs.getAttribute('data-salt');
    ITERATIONS=parseInt(gs.getAttribute('data-iterations'))||100000;
  }

  function b64ToBuf(b64){
    var bin=atob(b64);
    var arr=new Uint8Array(bin.length);
    for(var i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
    return arr;
  }

  function deriveKey(pass){
    var saltArr=b64ToBuf(B64_SALT);
    var enc=new TextEncoder();
    return crypto.subtle.importKey(
      "raw",enc.encode(pass),"PBKDF2",false,["deriveKey"]
    ).then(function(mat){
      return crypto.subtle.deriveKey(
        {name:"PBKDF2",salt:saltArr,iterations:ITERATIONS,hash:"SHA-256"},
        mat,{name:"AES-GCM",length:256},false,["decrypt"]
      );
    });
  }

  function decryptAndRender(key,b64,pass){
    var buf=b64ToBuf(b64);
    var iv=buf.slice(0,12);
    var tag=buf.slice(12,28);
    var ct=buf.slice(28);
    var tagged=new Uint8Array(ct.length+tag.length);
    tagged.set(ct);
    tagged.set(tag,ct.length);
    crypto.subtle.decrypt({name:"AES-GCM",iv:iv},key,tagged).then(function(dec){
      var html=new TextDecoder().decode(dec);
      if(pass)sessionStorage.setItem("gate-key",pass);
      document.open();document.write(html);document.close();
    }).catch(function(){
      sessionStorage.removeItem("gate-key");
      var err=document.getElementById("gate-error");
      if(err)err.textContent="Incorrect code. Try again.";
    });
  }

  function tryPass(pass){
    deriveKey(pass).then(function(key){
      decryptAndRender(key,window._enc,pass);
    }).catch(function(e){
      sessionStorage.removeItem("gate-key");
      var err=document.getElementById("gate-error");
      if(err)err.textContent="Incorrect code. Try again.";
    });
  }

  init();

  document.addEventListener("DOMContentLoaded",function(){
    var saved=sessionStorage.getItem("gate-key");
    if(saved&&window._enc){
      tryPass(saved);
    }
    var form=document.getElementById("gate-form");
    if(!form)return;
    form.addEventListener("submit",function(e){
      e.preventDefault();
      var pass=document.getElementById("gate-input").value;
      if(pass)tryPass(pass);
    });
  });
})();