var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        video: 'no_signal',
        image_capture:'/static/images/no_signal.jpg',
        camara: '',
        person_name: '',
        error_init: false,
        error_camara: false,
        error_name: false,
    },
    methods: {
    	clearData: function(){
    		this.error_name = false;
    		this.error_camara = false;
    		this.error_init = false;
    	},
    	checkData: function(){
    		this.clearData();
            if (this.camara === ""){ this.error_camara = true }
            if (this.person_name === ""){ this.error_name = true }
            if (this.error_name || this.error_camara){ return false } else{ return true}
    	},
        activeCapture: function(){
        	if (!this.checkData()){
        		return
        	}
        	this.image_capture = '/static/images/loading.gif';
            vue = this;
            var getCaptureFaceUrl = '/capture/face/name';
            var params = new URLSearchParams();
      		params.append('person_name', this.person_name);
      		params.append('camara_id', this.camara);
      		params.append('csrfmiddlewaretoken', jQuery("[name=csrfmiddlewaretoken]").val());
            axios.post(getCaptureFaceUrl, params)
            .then(function (response) {
                if (response.data.status == "success"){
                	vue.video = "loading";
                }
                if (response.data.status == "error"){
                	vue.error_init = true;
                	vue.image_capture = '/static/images/no_signal.jpg';
                }
            }).catch(function(error){
            	vue.error_init = true;
                vue.image_capture = '/static/images/no_signal.jpg';
            })
        },
        
    },
});