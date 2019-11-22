var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        person: [],
        empty_person: true,
        url_form: '',
        error_empty_name: false,
    },
    created: function(){
    },
    methods: {
        getPerson: function(pk){
            vue = this;
            if (this.person.fullname == ''){
    			this.error_empty_name = true;
    			return
    		}
            var getPersonUrl = 'get/person/'+pk+'/';
            axios.get(getPersonUrl)
            .then(function (response) {
                vue.person = response.data;
                vue.empty_person = false;
                vue.urlForm();
            })
        },
        urlForm: function(){
        	this.url_form = 'person/edit/'+this.person.id;
        },
    },
});