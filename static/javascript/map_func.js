let map, infoWindow;
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 35.30767025468232, lng: -80.73535463414414},
    zoom: 12,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    zoomControl: true,
    zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SAMLL
    }
    });
    infoWindow = new google.maps.InfoWindow();

    if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (position) => {
        const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
        };

        var user_marker = new google.maps.Marker({
            position: pos,
            title: "user_location",
            map: map
        });

        // call update_location function in app.py with pos as parameter
        $.ajax({
            type: "POST",
            url: "/update_location",
            data: JSON.stringify(pos),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
            console.log(data);
            },
            failure: function (errMsg) {
            console.log(errMsg);
            }
        });

        infoWindow.setPosition(pos);
        map.setCenter(pos);
        },
        () => {
        handleLocationError(true, infoWindow, map.getCenter());
        }
    );
    } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
    }
};

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
    browserHasGeolocation
        ? "Error: The Geolocation service failed."
        : "Error: Your browser doesn't support geolocation."
    );
    infoWindow.open(map);
}

window.initMap = initMap;
