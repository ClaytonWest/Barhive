let autocomplete;
let addressField;
let zipCodeField;

function initAutocomplete() {
  addressField = document.querySelector("#business_address");
  zipCodeField = document.querySelector("#zipcode");

  autocomplete = new google.maps.places.Autocomplete(addressField, {
    componentRestrictions: { country: ["us"] },
    fields: ["address_components", "geometry"],
    types: ["address"],
  });
  addressField.focus();

  autocomplete.addListener("place_changed", fillInAddress);
}

function fillInAddress() {

  const place = autocomplete.getPlace();
  let main_address = "";
  let zipcode = "";

  for (const component of place.address_components) {
    const componentType = component.types[0];

    switch (componentType) {
      case "street_number": {
        main_address = `${component.long_name} ${main_address}`;
        break;
      }

      case "route": {
        main_address += component.short_name;
        break;
      }

      case "postal_code": {
        zipcode = `${component.long_name}${zipcode}`;
        break;
      }

      case "locality": {
        document.querySelector("#locality").value = component.long_name;
        break;
      }

      case "administrative_area_level_1": {
        document.querySelector("#state").value = component.short_name;
        break;
      }

    }
  }

  addressField.value = main_address;
  zipCodeField.value = zipcode;

}

window.initAutocomplete = initAutocomplete;