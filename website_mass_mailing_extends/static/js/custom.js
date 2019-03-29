  $(document).ready(function () {
      var cont=0;
      $("#more_button").click(function() {
          cont++;
          /* var more = document.getElementById("more_child");
           var h1 = document.createElement("h1");
           h1.innerHTML = "hola mundo";
           more.appendChild(h1);*/

          $("#more_child").append("<div class=\"row form-group lines\">\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-5\" id=\"email\">\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-1 date\">\n" +
              "\t\t\t\t\t\t\t\t\t\t<input  name=\"day\" id=\"day\"  class=\"form-control\" placeholder=\"DD\" autofocus=\"autofocus\"/>\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-1 labels\">\n" +
              "\t\t\t\t\t\t\t\t\t\t<label>/</label>\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-1 date\">\n" +
              "\t\t\t\t\t\t\t\t\t\t<input name=\"month\" id=\"month\" class=\"form-control\" placeholder=\"MM\" autofocus=\"autofocus\"/>\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-1 labels\">\n" +
              "\t\t\t\t\t\t\t\t\t\t<label >/</label>\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t\t<div class=\"col-lg-1 date\">\n" +
              "\t\t\t\t\t\t\t\t\t\t<input  name=\"year\" id=\"year\" class=\"form-control\" placeholder=\"AAAA\" autofocus=\"autofocus\"/>\n" +
              "\t\t\t\t\t\t\t\t\t</div>\n" +
              "\t\t\t\t\t\t\t\t</div>");




          /* var gg=$("#gg");
            gg.data("id",(cont++).toString());*/

      })
  });