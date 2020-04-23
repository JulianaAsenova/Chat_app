document.addEventListener('DOMContentLoaded', () => {
	 var socket = io.connect('http://' + document.domain + ':' + location.port);

	socket.on('connect', () => {
		socket.send("I am connected");	
	});

	socket.on('message', data => {
		console.log(`Message recived: ${data}`)
		
		const p = document.createElement('p');
		const br = ocument.createElement('br');	
		p.innerHTML = data;
		document.querySelector('#display-message-section').append(p);
	});


	document.querySelector('#send_message').onclick = () => {
		socket.send(document.querySelector('#user_message').value)	
	}

})
