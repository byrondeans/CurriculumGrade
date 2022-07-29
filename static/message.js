document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    socket.on('connect', () => {

        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {	
		const selection = button.dataset.vote;
		const message = document.querySelector('#message').value;	
		const to_user = document.querySelector('#to_user').value;
		const username_to = document.querySelector('#username_to').value;
		socket.emit('submit message', {'msg': message, 'to_user': to_user, 'username_to': username_to});
	    	document.querySelector('#message').value = "";
	    };
	});
    });

    socket.on('message step', data => {
	const user_id_receiver = data['user_id_receiver'];
	const user_id_sender = data['user_id_sender'];
	const page_owner_id_from_div = document.getElementById('page_owner_id').innerHTML;
	const to_user_id_from_div = document.getElementById('to_user_id').innerHTML;
	
	if((user_id_sender == page_owner_id_from_div) || (user_id_receiver == page_owner_id_from_div) && (to_user_id_from_div == user_id_sender)) {
		socket.emit('look up messages', {'to_user': user_id_receiver, 'user_id_sender': user_id_sender});
	}
    });

    socket.on('display messages final', data => {
	document.querySelector('#messages').innerHTML = data.message;	
    });
});
