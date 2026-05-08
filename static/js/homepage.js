// Homepage JavaScript
let passengers = {
    adults: 1,
    children: 0,
    infants: 0,
    pets: 0
};

function togglePassengerModal() {
    const modal = document.getElementById('passengerModal');
    if (modal.style.display === 'flex') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'flex';
    }
}

function updatePassengers(type, delta) {
    if (type === 'adults') {
        const newValue = passengers.adults + delta;
        if (newValue >= 1) passengers.adults = newValue;
    } else if (type === 'children') {
        const newValue = passengers.children + delta;
        if (newValue >= 0) passengers.children = newValue;
    } else if (type === 'infants') {
        const newValue = passengers.infants + delta;
        if (newValue >= 0) passengers.infants = newValue;
    } else if (type === 'pets') {
        const newValue = passengers.pets + delta;
        if (newValue >= 0) passengers.pets = newValue;
    }
    
    // Update display
    document.getElementById('adultsCount').textContent = passengers.adults;
    document.getElementById('childrenCount').textContent = passengers.children;
    document.getElementById('infantsCount').textContent = passengers.infants;
    document.getElementById('petsCount').textContent = passengers.pets;
    
    // Update summary
    const total = passengers.adults + passengers.children + passengers.infants;
    document.getElementById('passengerSummary').textContent = `${total} passenger${total > 1 ? 's' : ''}`;
}

function searchTrips(event) {
    event.preventDefault();
    const from = document.getElementById('searchFrom').value;
    const to = document.getElementById('searchTo').value;
    const date = document.getElementById('searchDate').value;
    const totalPassengers = passengers.adults + passengers.children + passengers.infants;
    
    if (from && to && date) {
        window.location.href = `/login?redirect=search&from=${from}&to=${to}&date=${date}&passengers=${totalPassengers}&pets=${passengers.pets}`;
    } else {
        alert('Please fill in all fields');
    }
}
