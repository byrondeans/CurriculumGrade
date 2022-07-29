document.addEventListener('DOMContentLoaded', () => {

var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
socket.on('connect', () => {
        
        const comment = "from reply page";
        const to_video = "{{ video_id }}";
        
	socket.emit('submit comment', {'comment': comment, 'to_video': to_video});
    });

});
