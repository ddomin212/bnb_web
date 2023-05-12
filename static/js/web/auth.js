// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.4.1/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
} from "https://www.gstatic.com/firebasejs/9.4.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC6VkFrRH0WVlOcYL51ehPGK5l1Bb3D2Ts",
  authDomain: "bnb-ai.firebaseapp.com",
  projectId: "bnb-ai",
  storageBucket: "bnb-ai.appspot.com",
  messagingSenderId: "751285250326",
  appId: "1:751285250326:web:e377d97b60ef1bc9ca0837",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider(app);

async function setSession(email, password, name, type) {
  const result = await fetch("/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
      name: name,
      type: type,
    }),
  });
  window.location.replace("/");
}
loginGoogle.addEventListener("click", (e) => {
  e.preventDefault();
  signInWithPopup(auth, provider)
    .then((result) => {
      // This gives you a Google Access Token. You can use it to access the Google API.
      const credential = GoogleAuthProvider.credentialFromResult(result);
      const token = credential.accessToken;
      // The signed-in user info.
      const user = result.user;
      const gmail = user.email;
      const gpassword = user.uid;
      const gname = user.displayName;
      setSession(gmail, gpassword, gname, "google");
    })
    .catch((error) => {
      // Handle Errors here.
      const errorCode = error.code;
      const errorMessage = error.message;
      // The email of the user's account used.
      const email = error.email;
      // The AuthCredential type that was used.
      const credential = GoogleAuthProvider.credentialFromError(error);
      // ...

      alert(errorMessage);
    });
});
