async function fetchTips() {
  const request = await fetch(
    "/tips?city={{doc['city']}}&country={{doc['country']}}"
  );
  const tips = await request.json();
  const tipsList = document.getElementById("tips-list");
  tipsList.innerHTML = "";
  for (var i = 0; i < tips.travel_tips.length; i++) {
    tipsList.innerHTML += `
        <li class="list-item"><a href="https://www.bing.com/search?q=${tips.travel_tips[
          i
        ]
          .split(". ")[1]
          .replace(" ", "+")}">${tips.travel_tips[i]}</a></li>
        `;
  }
  console.log(tipsList);
}
//fetchTips();
function getStars() {
  var pStars = document.getElementById("stars");
  var rating = Number("{{avg_rating}}");
  var stars = "";
  for (var i = 0; i < Math.floor(rating); i++) {
    stars += '<i class="icon ion-star" style="font-size: 30px"></i>';
  }
  if (rating % 1 != 0) {
    if (rating - Math.floor(rating) > 0.5) {
      stars += '<i class="icon ion-ios-star-half" style="font-size: 30px"></i>';
    } else {
      stars +=
        '<i class="icon ion-android-star-outline" style="font-size: 30px"></i>';
    }
  }
  for (var i = Math.ceil(rating); i < 5; i++) {
    stars +=
      '<i class="icon ion-android-star-outline" style="font-size: 30px"></i>';
  }
  pStars.innerHTML = stars;
}
getStars();
