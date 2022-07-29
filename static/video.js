document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
		const comment = document.querySelector('#comment').value;
		const to_video = document.querySelector('#to_video').value;
		socket.emit('submit comment', {'comment': comment, 'to_video': to_video});
		document.querySelector('#comment').value = "";
		};
        });
    });

    // When a new vote is announced, add to the unordered list  {{ video_id }}
    socket.on('display comments', data => {
        if(data.video_id == 241) {
    	    document.querySelector('#comments').innerHTML = data.comments;
	}
    });
});
