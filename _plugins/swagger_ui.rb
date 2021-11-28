module Jekyll
  class SwaggerTag < Liquid::Tag
    @spec = nil

    def initialize(tag_name, markup, tokens)
      @spec = markup
      super
    end

    def render(context)
      id = Digest::MD5.hexdigest(@spec)
      # %Q{<div class="swagger-section"><div id="#{id}" class="swagger-ui"></div><script>$(function() { loadSwaggerUi("#{@spec}", "#{id}"); });</script></div>}

      # %Q{<div class="swagger-section"><div id="#{id}" class="swagger-ui"></div></div>}
      %Q{<div id="swagger-section" data-url="#{@spec}"><div id="swagger-ui"></div></div>}
    end
  end
end

Liquid::Template.register_tag('swagger', Jekyll::SwaggerTag)
