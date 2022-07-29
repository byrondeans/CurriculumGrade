document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
		const wallpost = document.querySelector('#wallpost').value;
		const wall_owner = document.getElementById('wall_owner_hidden_div').innerHTML;
		socket.emit('submit wall post', {'wallpost': wallpost, 'wall_owner': wall_owner});
		document.querySelector('#wallpost').value = "";
		};
        });
    });

    socket.on('display wall posts', data => {
    	document.querySelector('#wall_data').innerHTML = data.walldata;
	});

    socket.on('update wall broadcast true', data => {
	const wallpost = "";
	const wall_owner = document.getElementById('wall_owner_hidden_div').innerHTML;
	socket.emit('submit wall post', {'wallpost': wallpost, 'wall_owner': wall_owner});
    });


});
