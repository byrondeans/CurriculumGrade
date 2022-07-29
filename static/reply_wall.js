document.addEventListener('DOMContentLoaded', () => {

var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
socket.on('connect', () => {
        
        const comment = "from wall_post_replies page";
        const to_wall_post = "{{ wall_post_id }}";
        
	socket.emit('submit comment', {'comment': comment, 'to_wall_post': to_wall_post});
    });

});
