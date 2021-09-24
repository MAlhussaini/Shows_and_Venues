window.parseISOString = function parseISOString(s) {
    var b = s.split(/\D+/);
    return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};
if (location.pathname == "/artists/create") {
    alert('hey222!');
    document.getElementById("artist-form").onsubmit = function(e) {
        e.preventDefault();

        fetch('/artists/create', {
                method: 'POST',

                body: JSON.stringify({
                    'name': document.getElementById('name').value,
                    'city': document.getElementById('city').value,
                    'state': document.getElementById('state').value,
                    'phone': document.getElementById('phone').value,
                    // TODO: Configure genres
                    'genres': document.getElementById('genres').value,
                    'facebook_link': document.getElementById('facebook_link').value,
                    'image_link': document.getElementById('image_link').value,
                    'website_link': document.getElementById('website_link').value,
                    'seeking_venue': document.getElementById('seeking_venue').checked,
                    'seeking_description': document.getElementById('seeking_description').value
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(function(response) {
                return response.json();
            })
            .then(function() {
                window.location.href = "/";
            })
            .catch(function() {
                window.location.href = "/";
            })
    }

}
if (location.pathname == "/venues/create") {
    alert('hey!');
    document.getElementById("venue-form").onsubmit = function(e) {
        e.preventDefault();

        fetch('/venues/create', {
                method: 'POST',

                body: JSON.stringify({
                    'name': document.getElementById('name').value,
                    'city': document.getElementById('city').value,
                    'state': document.getElementById('state').value,
                    'address': document.getElementById('address').value,
                    'phone': document.getElementById('phone').value,
                    // TODO: Configure genres
                    'genres': document.getElementById('genres').value,
                    'facebook_link': document.getElementById('facebook_link').value,
                    'image_link': document.getElementById('image_link').value,
                    'website_link': document.getElementById('website_link').value,
                    'seeking_talent': document.getElementById('seeking_talent').checked,
                    'seeking_description': document.getElementById('seeking_description').value
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(function(response) {
                return response.json();
            })
            .then(function() {
                window.location.href = "/";
            })
            .catch(function() {
                window.location.href = "/";
            })
    }
}